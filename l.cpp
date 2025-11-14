#include<iostream>
using namespace std;
    int countOperations(int num1, int num2) {
        int count=0;
        int  diff=0;
        while((num1!=0)&&(num2!=0)){
            diff=ABS(num1-num2);
            if(num1>=num2){num1=diff;count++;}
            else {num2=diff;count++;}
           
        }
        return count;
    }
int main(){
    int num1,num2;
    cin>>num1>>num2;
    cout<<countOperations(num1,num2);
}