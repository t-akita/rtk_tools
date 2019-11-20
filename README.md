# ROS-Tk Tools  

## インストール
1. Tk-inter  
最古(?)のGUIフレームワークTcl/TkのPython版。Tclが手軽になった。
~~~
sudo apt-get install python-tk
~~~
2. tkfilebrowser  
ファイル管理Widgets
~~~
pip install tkfilebrowser --user
~~~
3. xterm  
単体node(.launch以外)はrosrunにて起動します。rosrunはxtermから起動しコンソール出力を識別し易くしています。
~~~
sudo apt install xterm
~~~

## 解説
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
