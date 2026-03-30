+++
draft = false
thumbnail = "2023/08/Function-Calls-With-and-Without-Virtual-in-Cpp/thumbnail.png"
tags = ["C/C++"]
categories = "プログラム"
date = "2023-08-22T04:12:13+09:00"
title = "virtualとそうでないときで呼び出す関数が変わる"
description = "virtualとそうでないときで呼び出す関数が変わる"
toc = true
archives = ["2023/08"]
+++

ベースクラスの関数をオーバーライドするのに、virtualの有無で挙動が変わることを確認したので、それについてまとめてみる。

実験のために下記を準備。オーバーライドしてBaseクラスのポインタに派生クラスのオブジェクトを入れている。
この状態でBaseクラスから派生クラスの関数を呼び出そうとする。

```cpp
class Base
{
public:
	void virtualFunction()
	{
		cout << "Base.virtualFunction()" << endl;
	}
};

class NewClass : public Base
{
	void virtualFunction()
	{
		cout << "NewClass.virtualFuction()" << endl;
	}

};

int main()
{
	Base *b = new NewClass();

	b->virtualFunction();　// 派生クラスの関数ではなくBaseクラスの関数が呼ばれてしまう

	delete b;

	return 0;
}
```

実際にはこれはNewClassの関数が呼ばれるのではなくBaseクラスの関数が呼ばれてしまう。
なので、オーバーライドして使ってほしい関数にはvirtual修飾子を付ける必要がある。

```cpp
class Base
{
public:
	void virtualFunction()
	{
		cout << "Base.virtualFunction()" << endl;
	}
};

class NewClass : public Base
{
	void virtualFunction()
	{
		cout << "NewClass.virtualFuction()" << endl;
	}

};

int main()
{
	Base *b = new NewClass();

	b->virtualFunction();　// 基底クラスのポインタから派生クラスの関数が呼べる

	delete b;

	return 0;
}
```

### まとめ

virtualをつけるときとつけないときで挙動が変わることを確認した。
クラスを作成して利用してもらう側の人は、virtualをつけてしっかり継承先で使ってもらうように作ろう。
逆に利用する側の人はvirtualと書かれている関数は、意図を組んでしっかりオーバーライドさせたい。

大体の場合はすでに出来ているものに対して機能を追加したりすることが多いと思うので、後者のケースが多いと思う。