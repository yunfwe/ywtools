function useproxy {
        export http_proxy="http://192.168.4.6:8088"
        export https_proxy="https://192.168.4.6:8088"
	if [[ \$1 == "out" ]];then
		export http_proxy="http://192.168.4.6:8089"
        	export https_proxy="https://192.168.4.6:8089"
	fi
}

function noproxy {
        unset http_proxy
        unset https_proxy
}
END
source /etc/profile.d/proxy.sh
echo "使用 useproxy 来通过国内代理上网"
echo "使用 useproxy out 来通过国外代理上网"
echo "使用 noproxy 取消代理设置"
