# ROS-Tk Tools

## Panel.md  

## パラメータ  
パラメータは、起動時の引数(args="...")かconfigパラメータ"/config/panel/..."によって設定します。両方に存在する場合は、"args"が優先されます。

|パラメータ名|機能|書式例|デフォルト|
|:----|:----|:----|:----|
|geom|パネルの表示位置、サイズ|"300x750-0+0"|←|
|weight|パネルの項目名列と値列の列幅比をTuple様の文字列で指定します|"(2, 1)"|←|
|lift|Trueのとき、パネルを強制的に前面に出します|True|←|
|message|保存ボタンを押した時の確認メッセージ|"Overwrite"|←|
|font/family|表示フォント名|"System"|←|
|font/size|フォントサイズ|10|←|
|color/background|背景色|"#00FF00"|←|
|conf|パネル設定ファイル名|"setup.zui"|なし|
|dump|保存先yamlファイル名|"param.yaml"|なし|
|dump_prefix|dumpファイルのプレフィックスを指定します|"WPC/recipe"|なし|
|dump_dir@|dumpファイル保存先ディレクトリを間接指定します|"/wpc/recipeName"|なし|
|dump_ver@|dumpファイル保存先ディレクトリのサブディレクトリのバーションを間接指定します|"/wpc/recipeNumber"|なし|

## Confファイル  
- テキスト形式のファイルにて、１行が表示項目の１行に対応する。
- 項目分類は以下の３種類
  - タイトル
  - パラメータ(Number,Text)
  - トピック表示(Echo)
  - パブリッシャ(Pub std_msgs/Boolのみ)
  
### Confファイル共通仕様  
Config fileは","で区切られた以下書式のテキストファイルです。
~~~
"<項目>:[<名前>]","表示内容"[,"オプション"]
~~~
"表示内容"が第1列Labelに表示されます。下記のようにこれに改行コード"\n"が含まれていた場合は、
~~~
"Echo:/robot/tf","位置 X\nY\nZ"
~~~
表示例3行目のように、行高さが(\n個数+1)倍されます。  
表示内容は原則的にLabel欄に**右寄せ表示**されます。

### タイトル  
タイトルの表示のみ、**1-2列に亘り左寄せ表示**されます。  
この表示に対応するConfig fileでの記述は下記となります。
~~~
"Title:","位相シフト用パラメータ"
~~~
### トピック表示    
この表示に対応するConfig fileでの記述は下記となります。
~~~
"Echo:gridboard/error","再投影誤差"
~~~

### 数値パラメータの表記  
この表示に対応するConfig fileでの記述は下記となります。
~~~
"Number:camera/ExposureTime","露光時間(usec)"
~~~

第2列を編集中は文字色が**赤**となり、変更イベントで値の書込が完了すると黒に戻ります(＜更新＞ボタンは削除)。


### 文字パラメータの表記  
この表示に対応するConfig fileでの記述は下記となります。
~~~
"Text:camera/ID","カメラID"
~~~

### パブリッシャの表記  
パブリッシャは、パラメータではなくトピックにパブリッシュ(std_msgs/Bool)します。
この表示に対応するConfig fileでの記述は下記となります。
~~~
"Publish:/rovi/X1","3D撮像"
~~~
＜実行＞ボタンを押すと、std_msgs/Boolをpublishします。  


## パラメータの保存  
パラメータ"dump"にてyamlファイルが指定されているときは、＜保存＞ボタンの操作により現在のパラメータを当該ファイルに書き込みます。前仕様との差異は
- 保存先yamlファイルに存在しないパラメータは追加しない

### dump_dir@  
以下のConfigパラメータ例にて説明します。
~~~
dump: "param.yaml"
dump_dir@: "recipeName"
~~~
"dump...@"はファイルの保存先をパラメータによって変更するための機能です。"dump_dir@"はディレクトリを変更します。上記例では、パラメータ"recipeName"にセットされている文字列を保存先ディレクトリとします。"recipeName"に"REINFORCE"がセットされていたとすると、保存先のファイルパスは"REINFORCE/param.yaml"に変更されます。

### dump_ver@  
先のConfigパラメータに"dump_ver@"が追加された場合で説明します。
~~~
dump: "param.yaml"
dump_dir@: "recipeName"
dump_ver@: "recipeNumber"
~~~
この用途は、先の"REINFORCE"ディレクトリに下記のサブディレクトリが存在し、その下に"param.yaml"が存在する場合です。
~~~
20191017-105722
20191017-105736
20191017-110554
~~~
このときパラメータ"recipeNumber"に数値1がセットされているとすると、保存先のファイルパスは"REINFORCE/20191017-105736/param.yaml"(2番目のサブディレクトリ)に変更されます。サブディレクトリの選択はサブディレクトリを昇順ソートした時のインデックスであることに注意してください。

### dump_prefix  
さらにConfigパラメータに"dump_prefix"が追加された場合
~~~
dump: "param.yaml"
dump_dir@: "recipeName"
dump_ver@: "recipeNumber"
dump_prefix: "WPC/recipe"
~~~
先に定めたファイルパスにprefixが前置され、ファイルパスは"WPC/recipe/REINFORCE/20191017-105736/param.yaml"となります。
