#include <iostream>
#include "makeDataBase.hpp"
#include "inputQuery.hpp"
#include "makeJson.hpp"
using namespace std;
int main() {
	CDataBase *db = new CDataBase;
	//db->build();
	CInputQuery *iq = new CInputQuery;
	CJson *js = new CJson;
	iq->readFile("./input.txt");
	iq->askWeight();
	js->makeJson();
	return 0;
}