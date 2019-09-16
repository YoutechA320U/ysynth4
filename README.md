## ysynth4

RaspberryPiとTimidity++を核にしたハードウェアシンセサイザーです。GM/GS/XG/エクスクルーシブのメッセージが使えます。

## ライセンス
ysynth4は複数のソフトウェアで構成されています。他のソフトウェアのライセンスはそのソフトウェアの元々のライセンスに準じます。ysynth4のソースコードそのものは[MITライセンス](https://github.com/YoutechA320U/ysynth4/blob/master/LICENSE)となっています。

## 概要
RaspberryPi 3B+で動作するハードウェアシンセサイザーです。チャンネルごとにデータを送信、ディスプレイに表示するMIDIコントローラとしての機能と、チャンネルごとにデータを受信、ディスプレイに表示し、任意のサウンドフォント(.sf2)を鳴らせるMIDI音源としての機能、任意のMIDIファイルを自身や外部音源で演奏できるMIDIシーケンサーとしての機能を持ちます。


![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/ysynth4.png "3Dイメージ")
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/ysynth4_hard.JPG "作例")
## スペック
    *GM/GS/XG/エクスクルーシブメッセージ対応*
    *Timidity++ version 2.14.0*
    
    システム:RaspberryPi 3B+, Raspbian buster Lite
    パート数:16
    最大同時発音数:128
    音源:サウンドフォント(.sf2) ※任意の数のファイルを追加可能
    サンプリングレート:32000Hz
    本体で操作、表示できるMIDIメッセージ:プログラムチェンジ、ボリューム、エクスプレッション、パン、モジュレーション、リバーブ、
                                      コーラス、ディレイ、ピッチベンド
    ディスプレイ:1.8インチ160x128フルカラーグラフィックディスプレイ
    接続端子:MIDI-IN/OUT、microUSBTypeB-MIDI端子、USB2.0TypeAx4(1つはUSBメモリ用)、イーサネット、3.5mmステレオオーディオ出力端子（本体orPi-DAC+）、RCA(Pi-DAC+)
    電源:DC5V2.4A
    シーケンサー:MIDIファイルを再生可能 ※任意の数のファイルを追加可能

## 開発環境
    OS : Raspbian buster Lite
    RaspberryPi : RaspberryPi 3B+
    Python : ver3.7
    
## 回路図
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/circuit.png "回路図")
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/ysynth4gb.png "ガーバーデータ")

ガーバーデータは[Ysynth4R2.2gb.zip](https://github.com/YoutechA320U/ysynth4/blob/master/Ysynth4R2.2gb.zip)にまとめてあります。各種サービスで発注可能です。
## 必要な部品

※基板やピンソケット、つまみ、取付ネジは除く

|部品名|型番など|数量|
|:---|:--:|---:|
|RaspberryPi|RaspberryPi 3B/3B+|1|
|Beetle - The Smallest Arduino Board|[DFR0282](https://www.switch-science.com/catalog/4284/)|1|
|micoSDカード|クラス10またはUHF-1以上かつ8GB以上|1|
|USBメモリ|FAT32でフォーマットが可能1GB以上|1|
|I2S接続オーディオDAC（オプション）|Pi-DAC+相当のDAC(Pi-DAC Zeroなど)|※オプション(1)|
|SPI接続128x160フルカラーグラフィックディスプレイ|ST7735|1|
|タクトスイッチ|[TVGP01-G73BBなど](http://akizukidenshi.com/catalog/g/gP-09826/)|6|
|1/4Wカーボン抵抗|220Ω|9|
||270Ω|2|
|発光ダイオード及び対応する抵抗|3mm+1/4W|2|
|セラミックコンデンサ|0.1μF|1|
|シュミットトリガインバーターIC|74HC14|2|
|スイッチングダイオード|[1N1418](http://akizukidenshi.com/catalog/g/gI-00941/)など|2|
|フォトカプラ|[TLP785](http://akizukidenshi.com/catalog/g/gI-07554/)|2|
|DIN-5ソケット(メス)|[KDJ103-5](http://akizukidenshi.com/catalog/g/gC-09565/)など|2|
## インストール方法
※OSはRaspbian buster Lite前提です。

1. Beetle - The Smallest Arduino Boardには[こちらのUSB-MIDI変換プログラム](https://github.com/gdsports/MIDIUARTUSB)を書き込んでください。

2. RaspberryPiをネットワークに接続して以下のコマンドを実行します。

    sudo apt-get update

    sudo apt-get upgrade -y

    sudo apt-get install -y git
    
    git clone --recursive --depth 1 https://github.com/YoutechA320U/ysynth4.git

3. `sudo sh /home/pi/ysynth4/setup.sh`でセットアップスクリプトを実行します。完了すると自動的に再起動します。

4. ディスプレイが表示されたら完了です。


## 使い方
Ysynth4基板とRaspberryPiを接続し、RaspberryPiにFAT32でフォーマットしたUSBメモリを接続します。
電源投入直後MIDI-OUTのLEDが一瞬点灯し、ディスプレイ全体が白く発光します。
しばらくするとディスプレイに「Ysynth4」の文字が上から降りてくる起動画面が表示されます。USBメモリが認識できていない場合は文字の代わりに四角が降ってきます。
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp01.JPG "BOOT_1")
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp02.JPG "BOOT_2")
起動画面の後後述の「MIDIコントローラモード」の画面が表示されたら操作可能になります。

## 操作方法
基本的に十字キーの上下で項目の選択、左右キーで項目の値を操作し、MODEキーを押しながらだと別の動作をします。
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp00.JPG "キー")
MODEキーを押しながら左右キーを押すと後述のモードを切り替え、MODEキーを押しながら上下キーだと本体の音量を調整します。

もし液晶に何も映らなくなった場合はMODEキーを押しながら他のキーを全て押してください。液晶があ初期化されて表示が復活します。
### MIDIコントローラモード
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp03.JPG "MIDIコントローラモード")
起動時に選択されているモードです。

チャンネル、プログラムチェンジ、ボリューム、エクスプレッション、パン、モジュレーション、リバーブ、コーラス、ディレイ、ピッチベンドの値を操作します。操作した値は本体音源とMIDI-OUT、USB-MIDI-OUTに反映されます。またUSB-MIDI機器を接続している場合その機器にも反映されます。逆にMIDI-INなどから本体にMIDIメッセージを受信した場合そのメッセージがディスプレイに反映されます。また、OKキーを押すと全チャンネルにノートオフメッセージが送信されます。

### SMFモード
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp04.JPG "SMFモード")
サウンドフォントの選択とSMF（標準MIDIファイル）の再生を行います。

サウンドフォントを左右キーで選択しOKキーを押すとそのサウンドフォントが選択されます。選択されたサウンドフォントの項目には「♪」が表示されます。サウンドフォントが選択されている場合、どのモードでもYsynth4はMIDI音源として機能します。MIDIコントローラモード、SMF再生及びMIDI-IN、USB-MIDI-INからのデータを受信し、またUSB-MIDI機器を接続している場合その機器からも受信します。

SMFの再生は同じく左右キーで選択し、OKキーで再生します。再生時には「▶」が表示されます。再生中にもう一度OKキーを押すと停止します。データの送信範囲はMIDIコントローラモードと同じです。
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp05.JPG "SMFモード")
それぞれの項目で表示されるデータはUSBメモリ内の/sf2/フォルダと/midi/フォルダを参照しています。フォルダが存在しない場合は自動的に生成します。また、もし/sf2/フォルダに"FluidR3_GM.sf2"が存在しない場合自動的にコピーします。Ysynth4のメモリは1GBなのでサウンドフォントは1つあたり500MB程度にしてください。対応していないサウンドフォントの場合は選択できないまたは、選択しても音が出ません。

サウンドフォントの重ね掛けは標準ではできませんが、サウンドフォント定義ファイルはUSBメモリの/timidity_cfg/に生成されています。もしそれが書き換えられるのなら重ね掛けも可能です。ただし、/timidity_cfg/フォルダと/sf2/フォルダのファイル名が一致しない場合、一致しないサウンドフォント定義ファイルは削除されます。

### 設定モード
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp07.JPG "設定モード")
各種設定を行います。他のモードより操作が複雑なので各項目の説明します。

#### WiFi
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp08.JPG "WiFi")

後述のオンラインアップデートでネットワークに接続する時に使います。項目には現在接続しているアクセスポイント名が表示されます。
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp09.JPG "WiFi")
項目でOKキーを押すとアクセスポイントのスキャンが始まり、アクセスポイントの選択画面になります。(アクセスポイントが存在しているのに直ぐに「見つかりませんでした」と出る場合はしばらく時間を空けてから実行してください)そこで更に左右キーで選択してOKキーを押すと、キーボードが出現し、パスワードの入力画面になります。
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp10.JPG "WiFi")
十字キーで選択しOKキーで入力します。「BS」を押すと1文字削除し、「↩」を押すと入力完了し、設定モードに戻ります。設定したパスワードは保持されますがパスワードが8文字未満または64文字以上の場合設定は保持されず、以前の設定がある場合それに戻されます。またパスワードが空の場合、その設定は削除されます。
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp11.JPG "WiFi")

##### Audio
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp12.JPG "Audio")
オーディオ出力先を選択します。項目には現在の出力先が表示されます。

OKキーを押すとbcm2835（内蔵出力）かIQaudioDAC（Pi-DAC+系）に変更するかのダイアログボックスが出現します。左右キーで選択し、OKキーで決定します。「はい」で出力先を変更した場合、強制的に再起動し、変更が適用されます。

#### USBメモリ
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp13.JPG "USB")
USBメモリの取り出し、認識の時に必ず行います。

OKキーを押すと取り出すか認識させるかのダイアログボックスが出現します。左右キーで選択し、OKキーで決定します。取り出す場合前述のサウンドフォントの選択やSMFの再生が強制的に解除、停止します。

#### Ysynth4アップデート
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp14.JPG "UPDATE")
Ysynth4の本体スクリプトysynth4.pyを最新版にアップデートします。

有線LANかWiFiでインターネットに接続してある必要があります。ダイアログボックスが出現し、左右キーで選択し、OKキーで決定します。
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp15.JPG "UPDATE")
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/disp16.JPG "UPDATE")
アップデート出来た場合、後述のリロードが行われます。

#### 再起動
本体の再起動を行います。ダイアログボックスが出現し、左右キーで選択し、OKキーで決定します。

#### シャットダウン
本体のシャットダウンを行います。ダイアログボックスが出現し、左右キーで選択し、OKキーで決定します。
ディスプレイ全体が白く発光し、MIDI-OUTのLEDが点灯してから電源を抜いてください。

#### リロード
Ysynth4の本体スクリプトのみ再起動します。ダイアログボックスが出現し、左右キーで選択し、OKキーで決定します。

## 備考

### 参考コード・資料
 * <http://artteknika.hatenablog.com/entry/2017/04/28/185509>  
 * <https://github.com/pimoroni/st7735-python>  
 * <https://github.com/SpotlightKid/python-rtmidi> 
 * <https://github.com/YoutechA320U/ttymidi> 
 * <http://d.hatena.ne.jp/kakurasan/20080409/p1>
 * <https://www.raspberrypi.org/forums/viewtopic.php?t=192291#p1280234>
 * <http://yueno.net/xoops/modules/xpwiki/?PC%2FRaspberryPi%2FLinux%E3%82%92%E5%8B%95%E3%81%8B%E3%81%97%E3%81%A6%E3%81%BF%E3%82%8B%2FUSB%E3%83%A1%E3%83%A2%E3%83%AA%E3%81%AE%E8%87%AA%E5%8B%95%E3%83%9E%E3%82%A6%E3%83%B3%E3%83%88>

## 履歴
    [2019/08/23] - 初回リリース(Ver.1.1)
    [2018/08/24] - 調整(Ver.1.2)
    [2018/08/25] - 調整(Ver.1.3)、README.mdを編集
    [2018/09/06] - 調整(Ver.1.6)    
    [2018/09/07] - WiFi設定機能を追加(Ver.1.75)、README.mdを編集
    [2018/09/09] - WiFi設定機能を修正(Ver.1.8)、README.mdを編集
    [2018/09/11] - ガーバーデータを追加(Rev.2.2)
    [2018/09/13] - 描画のマルチスレッド化(Ver.1.9)
    [2018/09/14] - 描画のマルチスレッド化調整及びディスプレイフリーズ対策追加(Ver.1.91)