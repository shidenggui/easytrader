#!/usr/bin/env perl
#===============================================================================
#
#         FILE: ht.pl
#
#        USAGE: ./ht.pl
#
#  DESCRIPTION:
#
#      OPTIONS: ---
# REQUIREMENTS: ---
#         BUGS: ---
#        NOTES: ---
#       AUTHOR: YOUR NAME (),
# ORGANIZATION:
#      VERSION: 1.0
#      CREATED: 2014/05/26 10时03分57秒
#     REVISION: ---
#===============================================================================

use strict;
use warnings;
use utf8;
use DBI;
use AnyEvent;
use AnyEvent::HTTP;
use Encode;
use HTTP::Date;
use DateTime;
use Date::Calc qw(Days_in_Month);
use POSIX qw(strftime);
use JSON;
use Data::Dumper;
use LWP;
use HTTP::Cookies;
use Mozilla::CA;
use FindBin qw($Bin);
use MIME::Base64;
use 5.010;
chdir($Bin);




my $ua = LWP::UserAgent->new();

$ua->ssl_opts( SSL_ca_file => Mozilla::CA::SSL_ca_file(),verify_hostname=>0 );

my $some_file = 'c.lwp';

$ua->cookie_jar(HTTP::Cookies->new());

#my $res= $ua->post('https://xueqiu.com/service/poster', [ 'url'=>'/provider/oauth/token','data[username]'=>'littlepanic72@gmail.com','data[areacode]'=>'86','data[telephone]'=>'','data[remember_me]'=>'1','data[password]'=>'9C04360BC0ACBDB16321D238F418DCA2','data[access_token]'=>'KLXqxlg6wbC9U2XdWJ0Yin','data[_]'=>rand(10000000)]); #多加了一个被发送的数据的数组



#userType=jy&loginEvent=1&trdpwdEns=7f0bad1d159636a7c1067e0258a5fced&macaddr=84%3A34%3A97%3A21%3AA8%3AA3&hddInfo=WD-WX31C32M1910+++++
#&lipInfo=10.249.3.123+10.81.120.168+&topath=null&accountType=1&userName=22222222&servicePwd=111111&trdpwd=7f0bad1d159636a7c1067e0258a5fced&vcode=CHXA

my (%money,@stocks,@t,@clist,$max_to_buy);
my ($acctSH,$acctSZ,$login);

my $userType =	"jy";
my $loginEvent	=	1;
my $trdpwdEns	=	"";
my $macaddr	=	"";
my $hddInfo	=	"WD-WX31C32M1910";
my $lipInfo	=	"";
my $topath	=	"null";
my $accountType	=	1;
my $userName =	"";
my $servicePwd	=	"";
my $trdpwd	=	"";
my $vcode = "";
my $tradehost ="https://tradegw.htsc.com.cn/?";
my $version =1;
my $op_entrust_way = 7;

my $url="https://service.htsc.com.cn/service/loginAction.do?method=login";

$ua->get("https://service.htsc.com.cn/service/login.jsp?logout=yes");

Init();
Login();
GET_FUNDS();
#STOCK_SALE('601166','16.8','20000');
#STOCK_BUY('150181','0.76',2000000);
#GET_STOCK_POSITION();
#GET_CANCEL_LIST();
#STOCK_CANCEL(333);
#say GET_MAXQTY_B('601166','16.55');
CL();

=cut
foreach my $i( 0..scalar(@{$stocks})-1)
		{
			say @{$stocks}[$i]->{stock_code} unless not exists @{$stocks}[$i]->{stock_code} ;
		}

@t = @$stocks;
foreach my $j( 0 .. scalar(@t)-1)
{
	 say $t[$j]->{stock_code} unless not exists $t[$j]->{stock_code};
}

=cut


sub GET_CANCEL_LIST
{
	my $function_id= 401;
	my $request_num = 300;
	my $url = "uid=$login->{uid}&cssweb_type=GET_CANCEL_LIST&version=$version&custid=$login->{account_content}&op_branch_no=$login->{branch_no}&branch_no=$login->{branch_no}&op_entrust_way=$op_entrust_way&op_station=$login->{op_station}&function_id=$function_id=&fund_account=$login->{account_content}&password=$login->{trdpwd}&identity_type=&exchange_type=&stock_account=&stock_code=locate_entrust_no=&query_direction=&sort_direction=0&request_num=$request_num&position_str=&ram=".rand(1);

	my $obj = GetUrl($url);

	if (  not defined($obj) or $obj->{cssweb_code} ne "success" ) {
		say "data error \tcssweb_code => $obj->{cssweb_code}";
		#进行异常处理
	}
	else
	{
		#$return = $obj->{item}[0]->{entrust_no};
	    undef(@clist);
		foreach my $i( 0..scalar(@{$obj->{item}})-1)
		{
#say "hell0";
			push @clist, @{$obj->{item}}[$i] unless not exists @{$obj->{item}}[$i]->{stock_code} ;

		}
#		say scalar(@clist);

		foreach my $i ( 0.. @clist-1)
		{
			say $clist[$i]->{stock_code};
		}

	}


}

sub GetUrl
{
	my $url = shift;
	$url= encode_base64($url,"");
	#say $url;

	my $r =$ua->get("$tradehost$url");
	my $decode = decode_base64($r->content);
	#say $decode;

	my $json = new JSON;
	my $obj;
	eval { $obj = $json->decode($decode); };
#return undef unless defined($obj);

	return $obj;

}
sub STOCK_CANCEL
{
	my $entrust_no = shift;
	my $batch_flag = shift || 0;
	my $function_id=304;
	my $request_num = 300;
	my $url = "uid=$login->{uid}&cssweb_type=STOCK_CANCEL&version=$version&custid=$login->{account_content}&op_branch_no=$login->{branch_no}&branch_no=$login->{branch_no}&op_entrust_way=$op_entrust_way&op_station=$login->{op_station}&function_id=$function_id=&fund_account=$login->{account_content}&password=$login->{trdpwd}&identity_type=&batch_flag=$batch_flag&exchange_type=&entrust_no=$entrust_no&ram=".rand(1);

	my $obj = GetUrl($url);

	if (  not defined($obj) or $obj->{cssweb_code} ne "success" ) {
		say "data error \tcssweb_code => $obj->{cssweb_code} ";
		#进行异常处理
		return -1;
	}
	else
	{

		return  $obj->{item}[0]->{entrust_no};
=cut
		foreach my $i( 0..scalar(@{$obj->{item}})-1)
		{
			push @clist, @{$obj->{item}}[$i] unless not exists @{$obj->{item}}[$i]->{stock_code} ;
		}
=cut
	}

}
sub STOCK_SALE
{
	my $code = shift;
	my $price = shift;
	my $amount = shift;
	my $stock_account = shift || "";
	my $exchange_type=0;

	if ($stock_account eq "") {
		if ($code =~/^1/ or  $code =~/^0/ or $code =~/^2/) {
			$stock_account =$acctSZ;
		}
		else
		{
			$stock_account =$acctSH;
		}
	}

	if ($stock_account eq $acctSH) {
		$exchange_type=1;
	}
	else
	{
		$exchange_type=2;

	}

	my $url = "uid=$login->{uid}&cssweb_type=STOCK_SALE&version=$version&custid=$login->{account_content}&op_branch_no=$login->{branch_no}&branch_no=$login->{branch_no}&op_entrust_way=$op_entrust_way&op_station=$login->{op_station}&function_id=302&fund_account=$login->{account_content}&password=$login->{trdpwd}&identity_type=&exchange_type=$exchange_type&stock_account=$stock_account&stock_code=$code&entrust_amount=$amount&entrust_price=$price&entrust_prop=0&entrust_bs=2&ram=".rand(1);

	#say $url;
	$url= encode_base64($url,"");
	#say $url;

	my $r =$ua->get("$tradehost$url");
	my $decode = decode_base64($r->content);
	#say $decode;

    my $return;

	my $json = new JSON;
	my $obj;
	eval { $obj = $json->decode($decode); };
		next unless defined($obj);

	if ($obj->{cssweb_code} ne "success" ) {
		say "data error \tcssweb_code => $obj->{cssweb_code}";
		#进行异常处理
		$return = $obj->{cssweb_code};
	}
	else
	{
		say "$obj->{item}[0]->{entrust_no} $code $price $amount";
		$return = $obj->{item}[0]->{entrust_no};
	}

   $return;

}


sub STOCK_BUY
{
	my $code = shift;
	my $price = shift;
	my $amount = shift;
	my $stock_account = shift || "";
	my $exchange_type=0;

	if ($stock_account eq "") {
		if ($code =~/^1/ or  $code =~/^0/ or $code =~/^2/) {
			$stock_account =$acctSZ;
		}
		else
		{
			$stock_account =$acctSH;
		}
	}
	if ($stock_account eq $acctSH) {
		$exchange_type=1;
	}
	else
	{
		$exchange_type=2;

	}



	my $url =

	"uid=$login->{uid}&cssweb_type=STOCK_BUY&version=$version&custid=$login->{account_content}&op_branch_no=$login->{branch_no}&branch_no=$login->{branch_no}&op_entrust_way=$op_entrust_way&op_station=$login->{op_station}&function_id=302&fund_account=$login->{account_content}&password=$login->{trdpwd}&identity_type=&exchange_type=$exchange_type&stock_account=$stock_account&stock_code=$code&entrust_amount=$amount&entrust_price=$price&entrust_prop=0&entrust_bs=1&ram=".rand(1);


	#say $url;
	$url= encode_base64($url,"");
	#say $url;

	my $r =$ua->get("$tradehost$url");
	my $decode = decode_base64($r->content);
	#say $decode;

    my $return;

	my $json = new JSON;
	my $obj;
	eval { $obj = $json->decode($decode); };
	if (not  defined($obj))
	{ say"error";	return "error"; } ;

	if ($obj->{cssweb_code} ne "success" ) {
		say "data error \tcssweb_code => $obj->{cssweb_code}";
		#进行异常处理
		$return = $obj->{cssweb_code};
	}
	else
	{
		say "$obj->{item}[0]->{entrust_no} $code $price $amount";
		$return = $obj->{item}[0]->{entrust_no};
	}



}


#暂时退市风险提醒
sub DELISTING_RISK
{
my $t = q!
uid=153-5c68-7523507&cssweb_type=DELISTING_RISK&version=1&custid=$login->{account_content}&op_branch_no=0802&branch_no=0802&op_entrust_way=7&op_station=IP$120.196.156.135;MAC$84-34-97-21-A8-A3;HDD$WD-WX31C32M1910     &function_id=330300&fund_account=$login->{account_content}&password=$login->{trdpwd}&identity_type=&query_type=0&exchange_type=&stock_type=&stock_code=150181&position_str=&request_num=1&ram=0.4756480357609689

{"cssweb_code":"success","cssweb_type":"DELISTING_RISK","item":[{"exchange_type":"2","stock_code":"150181","stock_name":"����A","buy_unit":"100","price_step":"1","delist_flag":"0","delist_date":"0"},{"cssweb_test":"0"}]}

!;
}

sub GET_MAXQTY_B
{

	my $code = shift;
	my $price = shift;
	my $stock_account = shift || "";

	my $exchange_type=0;
    say $code;
	say $price;

	if ($stock_account eq "")
	{
		if ($code =~/^1/ or  $code =~/^0/ or $code =~/^2/)
		{
			$stock_account =$acctSZ;
		}
		else
		{
			$stock_account =$acctSH;
		}
	}
	if ($stock_account eq $acctSH) {
		$exchange_type=1;
	}
	else
	{
		$exchange_type=2;

	}


		my $function_id=301;

		my $url = "uid=$login->{uid}&cssweb_type=GET_MAXQTY_B&version=$version&custid=$login->{account_content}&op_branch_no=$login->{branch_no}&branch_no=$login->{branch_no}&op_entrust_way=$op_entrust_way&op_station=$login->{op_station}&function_id=$function_id=&fund_account=$login->{account_content}&password=$login->{trdpwd}&identity_type=&exchange_type=$exchange_type&stock_account=$stock_account&stock_code=$code&entrust_price=$price&bk_enable_balance=-1&entrust_prop=0&ram=".rand(1);

#say $url;

	my $obj = GetUrl($url);
	if (  not defined($obj) or $obj->{cssweb_code} ne "success" ) {
		say "data error \tcssweb_code => $obj->{cssweb_code}";
		#进行异常处理
		$max_to_buy=-1;
	}
	else
	{
		#$return = $obj->{item}[0]->{entrust_no};
		$max_to_buy = @{$obj->{item}}[0]->{enable_amount};

	}


}

sub GET_TODAY_TRADE
{
my $t = q!
	uid=153-5c68-7523507&cssweb_type=GET_TODAY_TRADE&version=1&custid=$login->{account_content}&op_branch_no=0802&branch_no=0802&op_entrust_way=7&op_station=IP$120.196.156.135;MAC$84-34-97-21-A8-A3;HDD$WD-WX31C32M1910     &function_id=402&fund_account=$login->{account_content}&password=$login->{trdpwd}&identity_type=&serial_no=&exchange_type=&stock_account=&stock_code=&query_direction=1&request_num=100&query_mode=0&position_str=&ram=0.5748597849160433
	{"cssweb_code":"success","cssweb_type":
		"GET_STOCK_POSITION","item":
		!;
}

sub GET_STOCK_POSITION
{
=cut
{"exchange_type":"1","exchange_name":"�Ϻ���","stock_account":"A812773010","stock_code":"600000","stock_name":"�ַ�����","current_amount":"600.00","enable_amount":"600.00","last_price":"14.900","cost_price":"23.254","keep_cost_price":"23.254","income_balance":"-5012.12","hand_flag":"0","market_value":"8940.00","av_buy_price":"18.160","av_income_balance":"-3051.53"}
}
=cut
my $url ="uid=$login->{uid}&cssweb_type=GET_STOCK_POSITION&version=$version&custid=$login->{account_content}&op_branch_no=$login->{branch_no}&branch_no=$login->{branch_no}&op_entrust_way=$op_entrust_way&op_station=$login->{op_station}&function_id=403&fund_account=$login->{account_content}&password=$login->{trdpwd}&identity_type=&exchange_type=&stock_account=&stock_code=&query_direction=&query_mode=0&request_num=100&position_str=&ram=".rand(1);

	$url= encode_base64($url,"");
	#say $url;

	my $r =$ua->get("$tradehost$url");
	my $decode = decode_base64($r->content);
	#say $decode;

    my $return;

	my $json = new JSON;
	my $obj;
	eval { $obj = $json->decode($decode); };
	if (not  defined($obj))
	{ say"error";	return "error"; } ;

	if ($obj->{cssweb_code} ne "success" ) {
		say "data error \tcssweb_code => $obj->{cssweb_code}";
		#进行异常处理
		$return = $obj->{cssweb_code};
	}
	else
	{
		undef(@stocks);
		#$stocks = $obj->{item};

		foreach my $i( 0..scalar(@{$obj->{item}})-1)
		{
			push @stocks, @{$obj->{item}}[$i] unless not exists @{$obj->{item}}[$i]->{stock_code} ;
		}

	}
	@stocks;

}

sub GET_FUNDS
{
	my $version =	1;
	my $function_id	=	"405";
	my $tmpurl	=	"uid=$login->{uid}".'&cssweb_type=GET_FUNDS&version=1&custid=$login->{account_content}&op_branch_no=0802&branch_no=0802&op_entrust_way=7&op_station=$login->{op_station}function_id=405&fund_account=$login->{account_content}&password=$login->{trdpwd}&identity_type=&money_type=&ram='.rand(1);


	$tmpurl = encode_base64($tmpurl);
	$tmpurl=~ s/\n//gm;

	$tmpurl ="https://tradegw.htsc.com.cn/?$tmpurl";

	my $r =$ua->get(
	$tmpurl);
	#say $r->as_string;

	say "---------------------------------";


	my $decode = decode_base64($r->content);

	#say $decode;

=cut
	{"cssweb_code":"success","cssweb_type":"GET_FUNDS","item":[{"money_type":"0","money_name":"人民币","current_balance":"30.49","enable_balance":"41.77","fetch_balance":"30.49","market_value":"240005.00","asset_balance":"240069.48"},{"cssweb_test":"0"}]}
=cut
	my $json = new JSON;

	my $obj;
	eval { $obj = $json->decode($decode); };
		next unless defined($obj);

	if ($obj->{cssweb_code} ne "success" )
	{
		say "data error \tcssweb_code => $obj->{cssweb_code}";
		#进行异常处理
	}

	foreach my $i (0.. scalar(@{$obj->{item}})-1) #
	{
		if (not exists $obj->{item}[$i]->{money_type} or $obj->{item}[$i]->{money_type} != 0 ) {
			say "not RMB";
			next;
		}
		$money{current_balance} =$obj->{item}[$i]->{current_balance};
		$money{enable_balance} =$obj->{item}[$i]->{enable_balance};
		$money{fetch_balance} =$obj->{item}[$i]->{fetch_balance};
		$money{market_value} =$obj->{item}[$i]->{market_value};
		$money{asset_balance} =$obj->{item}[$i]->{asset_balance};
	}

	foreach my $k (keys %money) {
		say "$k\t=>\t$money{$k}";
	}
}

sub Login
{
	my $r =$ua->get("https://service.htsc.com.cn/service/login.jsp");
	#say $r->as_string;

	$ua->{cookie_jar}->extract_cookies($r);


my $url="https://service.htsc.com.cn/service/loginAction.do?method=login";
	$vcode = GetYZM();
	my $res =$ua->post($url,['userType'=>$userType,
						 'loginEvent'=>$loginEvent,
						 'trdpwdEns' =>$trdpwdEns,
						 'macaddr'=>$macaddr,
						 'hddInfo'=>$hddInfo,
						 'lipInfo'=>$lipInfo,
						 'topath' =>$topath,
						 'accountType'=>$accountType,
						 'userName'=>$userName,
						 'servicePwd'=>$servicePwd,
						 'trdpwd'=>$trdpwd,
						 'vcode'=>$vcode,
						 ]);
    my $c = $res->content;

	$c =decode("utf8",$c);

	if( not $c=~/欢迎您/ )
	{
		print "login fail\n";
		sleep(10);
		Login();
	}

	else
	{
		#say $res->as_string;
		$res = $ua->get('https://service.htsc.com.cn/service/jy.jsp?sub_top=jy');
		#print $res->content;
		#say $res->as_string;

		print "login\n";

		####进入交易页面~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		$res = $ua->get('https://service.htsc.com.cn/service/flashbusiness_new3.jsp?etfCode=');
		#print $res->content;
		#say $res->as_string;

		my $a;
		if ($res->content =~/var\s+data\s+=\s+"(.*?)";/) {
			$a=$1;
		}

		$a = decode_base64($a);
		#say $a;
		my $json = new JSON;

		eval { $login = $json->decode($a); };
		return unless defined($login);

		foreach my $i (0.. scalar(@{$login->{item}})-1) #
		{
			if ($login->{item}[$i]->{"exchange_type"} == 1 ) {
				$acctSH = $login->{item}[$i]->{"stock_account"};
			}
			else
			{
				$acctSZ = $login->{item}[$i]->{"stock_account"};
			}
		}
		#say $login->{uid};
	}
}

sub Init
{
	$userType =	"jy";
	$loginEvent	=	1;
	$trdpwdEns	=	"";
	$macaddr	=	"";
	$hddInfo	=	'WD-WX31C32M1910     ';
	$lipInfo	=	'';
	$topath	=	"null";
	$accountType	=	1;
	$userName =	"";
	$servicePwd	=	"";
	$trdpwd	=	"";
	$tradehost ="https://tradegw.htsc.com.cn/?";
	$version =1;

	$ua->get("https://service.htsc.com.cn/service/login.jsp");

}

sub GetYZM
{
	my $url='https://service.htsc.com.cn/service/pic/verifyCodeImage.jsp?ran='.rand(1);
	my $content = $ua->get($url);
	die "Couldn't get it!" unless defined $content;
	my $logo = 'logo.gif';
	#print $content->content;
	open FH, " > $logo" or die "Can't open $logo for saving!";
	binmode FH;
	print FH $content->content;
	close FH;
	`tesseract $logo A`;
    open FH , " < A.txt";
	my $code = <FH>;
	chomp($code);
	close FH;

	$code =~ s/\s//;
	$code =~ s/\>\</X/;
	print $code,"\n";
	$code

}
