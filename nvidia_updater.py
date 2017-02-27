#!/usr/bin/env python
#encoding=utf-8
"""
这个程序是自动检测当前的Nvidia显卡驱动的版本，并进行更新。写这个主要是由于官方的驱动 --update
在中国速度太慢了
"""
import datetime
import subprocess
import requests
import json
import os

def get_current_version():
    version = 0
    try:
        nvidia_install = subprocess.Popen(["nvidia-installer", "-v"], universal_newlines=True,
         stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        nvidia_install.wait()
        version = nvidia_install.stdout.readlines()[1].split(" ")[3]
    except:
        print("No nVidia Driver Found")
    return float(version)

def get_latest_version():
    res = requests.get("http://www.geforce.cn/proxy?proxy_url=http%3A%2F%2Fgfwsl.geforce.com"
        + "%2Fservices_toolkit%2Fservices%2Fcom%2Fnvidia%2Fservices%2FAjaxDriverService.php%3F"
        + "func%3DDriverManualLookup%26psid%3D98%26pfid%3D756%26osID%3D12%26languageCode%3D2052%26beta%3Dnull%26isWHQL"
        + "%3D0%26dltype%3D-1%26sort1%3D0%26numberOfResults%3D10")
    res = json.loads(res.content.decode("utf-8"))
    latest_version = 0
    latest_release_time = "0";
    target_download_url = ""
    for ID in res["IDS"]:
        ID = ID["downloadInfo"]
        if ID["ReleaseDateTime"] > latest_release_time:
            latest_release_time = ID["ReleaseDateTime"]
            latest_version = ID["Version"]
            target_download_url = ID["DownloadURL"]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    driver_filename = "nvidia_driver_{}.run".format(str(latest_version))
    now = datetime.datetime.now()
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.isfile(os.path.join(dir_path, "downloads", driver_filename)):
        DEVNULL = open(os.devnull, 'wb')
        print("Downloading New Driver {} Time: {}".format(latest_version, current_time_str))
        driver_downloader = subprocess.Popen(["wget", target_download_url, "-O",
            driver_filename], cwd=os.path.join(os.getcwd(), "downloads"), stdout=DEVNULL, stderr=DEVNULL)
        DEVNULL.close()
        driver_downloader.wait()
        now = datetime.datetime.now()
        current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        print("Download Driver {} Time: {}".format(latest_version, current_time_str))
    return float(latest_version)

def update_driver(latest_version):
    # 关闭gdm
    print("Stopping X Server")
    subprocess.call(["/bin/systemctl", "stop", "lightdm.service"])
    print("X Server Stopped")
    print("Installing New Driver {}".format(latest_version))
    dir_path = os.path.dirname(os.path.realpath(__file__))
    now = datetime.datetime.now()
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    driver_filename = "nvidia_driver_{}.run".format(str(latest_version),current_time_str)
    DEVNULL = open(os.devnull, 'wb')
    install_process = subprocess.Popen(["sh", os.path.join(dir_path, "downloads", driver_filename),
        "--dkms", "-s"], stdout=DEVNULL, stderr=DEVNULL)
    DEVNULL.close()
    install_process.wait()
    return install_process.returncode

def is_driver_installed():
    kernel_version_cmd = subprocess.Popen(["uname", "-r"], universal_newlines=True,
     stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    kernel_version_cmd.wait()
    kernel_version = kernel_version_cmd.stdout.readlines()[0][:-1]
    return os.path.isfile("/lib/modules/{}/kernel/drivers/video/fbdev/nvidia/nvidiafb.ko".format(kernel_version))

if __name__ == "__main__":
    current_version = get_current_version()
    latest_version = get_latest_version()
    installed_flag = is_driver_installed()
    if current_version != latest_version or not installed_flag:
        result = update_driver(latest_version)
        now = datetime.datetime.now()
        current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        if not result:
            print("Driver {} installed falied. Time: {}".format(str(latest_version), current_time_str))
            exit(-1)
        else:
            print("Driver {} installed successful. Time: {}".format(str(latest_version), current_time_str))
    else:
        print("Already installed the latest driver {}".format(str(latest_version)))
