#include "fvCFD.H"
#include "regionProperties.H"      // provides class regionProperties
#include <map>
#include <cmath>

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"

    // ─────────────────────────────────────────────────────────────
    // Read region properties (fluid / solid grouping)
    // ─────────────────────────────────────────────────────────────
    regionProperties rp(runTime);

    // Get fluid regions the correct way for your version
    wordList fluidRegionNames;
    if (rp.found("fluid"))
    {
        fluidRegionNames = rp["fluid"];   // or rp.lookup("fluid")
    }

    if (fluidRegionNames.empty())
    {
        FatalErrorInFunction
            << "No fluid regions defined in constant/regionProperties" << nl
            << "Check that your regionProperties has an entry like:" << nl
            << "regions" << nl
            << "(" << nl
            << "    fluid (fluid)" << nl
            << "    solid (solid)" << nl
            << ");" << nl
            << abort(FatalError);
    }

    // Hardcoded: we want to process the region named "fluid"
    word fluidRegionName = "fluid";

    bool found = false;
    forAll(fluidRegionNames, i)
    {
        if (fluidRegionNames[i] == fluidRegionName)
        {
            found = true;
            break;
        }
    }

    if (!found)
    {
        FatalErrorInFunction
            << "Requested fluid region '" << fluidRegionName << "' not found." << nl
            << "Available fluid regions: " << fluidRegionNames << nl
            << abort(FatalError);
    }

    // ─────────────────────────────────────────────────────────────
    // Create mesh for the fluid region
    // ─────────────────────────────────────────────────────────────
    Info<< nl
        << "Creating mesh for fluid region: " << fluidRegionName << nl << endl;

    fvMesh fluidMesh
    (
        IOobject
        (
            fluidRegionName,
            runTime.timeName(),
            runTime,
            IOobject::MUST_READ
        )
    );

    // ─────────────────────────────────────────────────────────────
    // Read velocity and temperature fields in the fluid region
    // ─────────────────────────────────────────────────────────────
    Info<< "Reading velocity field U in region " << fluidRegionName << nl << endl;
    volVectorField U
    (
        IOobject
        (
            "U",
            runTime.timeName(),
            fluidMesh,
            IOobject::MUST_READ,
            IOobject::NO_WRITE
        ),
        fluidMesh
    );

    Info<< "Reading temperature field T in region " << fluidRegionName << nl << endl;
    volScalarField T
    (
        IOobject
        (
            "T",
            runTime.timeName(),
            fluidMesh,
            IOobject::MUST_READ,
            IOobject::NO_WRITE
        ),
        fluidMesh
    );

    // ─────────────────────────────────────────────────────────────
    // Compute bulk temperature along x-direction
    // ─────────────────────────────────────────────────────────────
    Info<< nl
        << "Computing mass-flow-weighted temperature along x (fluid region only)" << nl << endl;

    std::map<double, double> sumUTV;   // ∑ (u_x * T * V)
    std::map<double, double> sumUV;    // ∑ (u_x * V)

    const scalar eps = 1e-6;           // tolerance for grouping x-positions

    forAll(fluidMesh.C(), celli)
    {
        const vector& Cc = fluidMesh.C()[celli];
        scalar x = Cc.x();

        // Round to group cells belonging to approximately same x-plane
        scalar xKey = std::round(x / eps) * eps;

        scalar ux   = U[celli].x();
        scalar temp = T[celli];
        scalar vol  = fluidMesh.V()[celli];

        sumUTV[xKey] += ux * temp * vol;
        sumUV[xKey]  += ux * vol;
    }

    // ─────────────────────────────────────────────────────────────
    // Write output file
    // ─────────────────────────────────────────────────────────────
    OFstream bulkFile("bulkTemp.dat");

    if (!bulkFile.good())
    {
        FatalErrorInFunction
            << "Cannot open bulkTemp.dat for writing" << nl
            << exit(FatalError);
    }

    bulkFile << "# x [m]          T_bulk [K]" << nl;
    bulkFile << "# T_bulk = Σ(u_x * T * V) / Σ(u_x * V)   per x-slice" << nl;
    bulkFile << "# (assumes dominant flow direction +x)" << nl << nl;

    label nWritten = 0;
    for (const auto& entry : sumUV)
    {
        scalar xKey   = entry.first;
        scalar sumUV_ = entry.second;

        auto it = sumUTV.find(xKey);
        if (it == sumUTV.end()) continue;

        scalar sumUTV_ = it->second;

        if (mag(sumUV_) > 1e-12)   // avoid div-by-zero or negligible flow
        {
            scalar Tbulk = sumUTV_ / sumUV_;
            bulkFile << xKey << "   " << Tbulk << nl;
            nWritten++;
        }
    }

    Info<< nl
        << "Written " << nWritten << " x-locations to bulkTemp.dat" << nl
        << "Number of distinct planes found: " << sumUV.size() << nl << endl;

    Info<< "\nEnd\n" << endl;

    return 0;
}   
