
#include "pin.H"
#include <iostream>
#include <iomanip>
#include <fstream>
#include <set>
#include <map>
#include <string>

std::ostream * out = &cerr;
ofstream outFile;
string fileName;

std::map<string, std::set<ADDRINT> *> bbls;

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE,  "pintool",
    "o", "", "specify the file which should contains the bbls");

INT32 Usage()
{
    cerr << "This tool saves all touched basic blocks of an application in a file" << endl << endl;

    cerr << KNOB_BASE::StringKnobSummary() << endl;

    return -1;
}


VOID PIN_FAST_ANALYSIS_CALL LogBBL(ADDRINT addr)
{
    PIN_LockClient();
    IMG img = IMG_FindByAddress(addr);

    PIN_UnlockClient();
   
    if (IMG_Valid(img)){
        std::set<ADDRINT> *s = bbls[IMG_Name(img)];
        if (s == NULL){
            
            s = new std::set<ADDRINT> ();
            bbls[IMG_Name(img)] = s;

        }
        s->insert(addr - IMG_LowAddress(img));
    }

    
      
}


VOID Trace(TRACE trace, VOID *v)
{
    for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl))
    {
        BBL_InsertCall(bbl, IPOINT_ANYWHERE, (AFUNPTR)LogBBL, IARG_FAST_ANALYSIS_CALL, IARG_ADDRINT, BBL_Address(bbl), IARG_END);
    }
}



VOID Fini(INT32 code, VOID *v)
{
    
    outFile.open(fileName.c_str(),ios::out);
    for (std::map<string,std::set<ADDRINT> *>::iterator it=bbls.begin(); it!=bbls.end(); ++it){
        outFile << it->first << ": ";
        
        for (std::set<ADDRINT>::iterator its=it->second->begin(); its!= it->second->end(); ++its)
            outFile << *its << ",";
       
        outFile << "\n";
        outFile.flush();
    }
    outFile.close();
}


int main(int argc, char *argv[])
{
    if( PIN_Init(argc,argv) )
    {
        return Usage();
    }
    
    fileName = KnobOutputFile.Value();

    if (fileName.empty()) { return Usage();}
    
    TRACE_AddInstrumentFunction(Trace, 0);

    PIN_AddFiniFunction(Fini, 0);
    PIN_StartProgram();

    return 0;
}
