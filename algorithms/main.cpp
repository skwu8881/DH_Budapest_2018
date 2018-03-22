#include <iostream>
#include "makeDataBase.hpp"
#include "inputQuery.hpp"
using namespace std;
int main() {
	CDataBase *db = new CDataBase;
	//db->build();
	CInputQuery *iq = new CInputQuery;

	iq->readFile("./input.txt");
	iq->askWeight();
	return 0;
}