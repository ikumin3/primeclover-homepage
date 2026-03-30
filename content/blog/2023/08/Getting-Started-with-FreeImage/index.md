+++
draft = false
thumbnail = "2023/08/Getting-Started-with-FreeImage/thumbnail.png"
tags = ["C/C++","プログラム"]
categories = "プログラム"
date = "2023-08-18T11:49:19+09:00"
title = "FreeImageを使ってみる"
description = "FreeImageを使ってみる"
toc = true
archives = ["2023/08"]
+++

# FreeImageを使ってみる

C++で画像を読み込んで遊んでみたいなと思ったので、色々ある画像ライブラリの中から、FreeImageというライブラリを使って色々試してみようと思って導入してみました。

…なんだけど、FreeImageのサンプルであるBatchLoadがそのままだと動かなかったので、その解決策も含めて学んだことをここにまとめてみます。

## FreeImageとは

![Untitled](Untitled.png)

最初に行ったように、画像読み込みライブラリの一つ。
他には[ここ](https://qiita.com/ohwada/items/8703ede811476dd9c47f)で語られてるように、DevilとかOpenCVとかあるっぽい。

多分OpenCVよりは軽量な感じはする。OpenCVはだいぶ多機能なので、読み込んで変換するぐらいであればこれで問題なさそう。

## ダウンロード

まずはWindows用のビルド済みのライブラリを取得しに行きます。
DLLのファイルをダウンロードして解凍すると、ヘッダーファイルとlib,dllファイルが手に入ります。
取得したFreeImageディレクトリは適当に開発しているプロジェクトの直下に移動しておきます。

![Untitled](Untitled%201.png)

## 環境構築

開発環境はVisualStudio2022でやってます。まずはインクルードとリンカ設定。
構成とプラットフォームには気をつけてください。

### インクルード

私の場合はプロジェクトディレクトリにlibディレクトリを作成して、その中にFreeImageを追加しました。
こんな感じで設定。

![Untitled](Untitled%202.png)

### リンカ

リンカもおんなじように設定。

![Untitled](Untitled%203.png)

![Untitled](Untitled%204.png)

これで下準備は完了です。

## サンプルプログラム（BatchLoad.cpp）を用意

ダウンロードしたFreeImageのディレクトリに、Example/Generic/BatchLoad.cppがあるはずなので、これを開きます。
このサンプルは指定したディレクトリの中の画像ファイルをLoadして、一括でpngに変換するプログラムになってます。

早速開いたら、input_dirを変換したい画像が含まれているディレクトリパスに変更します。

これで実行…できれば良いですが、おそらくwhile (_findnext(handle, &finddata) == 0);あたりでメモリ外アクセスエラーが出ると思います。

input_dirはlong型になってますが、こちらをintptr_t型に変更しておきます。どうやら_findfirstが返す値がintptr_tになってるようで、Windowsの場合、long型のままだと32bitなので、帰ってくる値次第ではマイナスになっちゃうので、その後の_findnextでエラーになるようです。

intptr_t型はプラットフォーム依存しないので、とりあえずこちらで受け取っておけば問題なく動くかと思います。

```cpp
long handle;

↓

intptr_t handle;
```

これで指定したディレクトリの中にある画像郡はプロジェクト直下で1,2,3…pngになってるはず。

## まとめ

- 画像読み込みライブラリであるFreeImageの導入についてまとめた
- サンプルプログラムのBatchLoad.cppを修正して一括変換出来るようにした。

まさか戻ってくる型が異なっていて、それでメモリ外アクセスエラーを起こしてるとは思わず、特定するのに時間がかかりました…

デバッグ時にマイナスになっていたら、型違いというのは疑ったほうが良いですねー。
ライブラリの導入も学べて結構勉強になったし、今後は他のライブラリも追加してプログラム組めそうかも。