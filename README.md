# ROS-Tk Tools  

## Library
### dictlib  
dictlibは2つの辞書の合成を行うライブラリです。呼出し書式は以下のようになります。
~~~  
dictlib.func(A,B)    
~~~
dictlibのメソッドは、A,Bという２つの辞書を所定の規則にて辞書Aに合成します。dictlibのメソッドを以下に一覧します。  

|Method|Equation|Figure|
|:----|:----|:----|
|merge|C=A&cap;B<br>A=(A&frasl;C)&cup;B|![merge](icon/merge.png)|
|cross|C=A&cap;B<br>A=(A&frasl;C)&cup;(B&frasl;C)<sup>C</sup>|![cross](icon/cross.png)|

### rtk???  
rtkクラス群はpanelを構成するクラスです。

## Application
### panel
### dashboard