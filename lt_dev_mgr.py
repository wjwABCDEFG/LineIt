# -*- coding: utf-8 -*-
"""
@Time    : 2025/1/7 15:26
@Author  : wenjiawei
"""
import os
import re
import subprocess
import time
import traceback
from threading import Thread

from pymobiledevice3 import usbmux

DEBUG = False
PLAT_ANDROID = 'Android'
PLAT_IOS = 'iOS'


class _Helper:
    @staticmethod
    def listDevice():
        raise NotImplemented

    @staticmethod
    def installApp(deviceid, package_name: str):
        raise NotImplemented

    @staticmethod
    def launchApp(deviceid, package_name: str):
        raise NotImplemented

    @staticmethod
    def captureScreen(deviceid, file_path: str = None):
        raise NotImplemented

    @staticmethod
    def get_memory_usage(deviceid, package_name: str = None):
        """获取内存使用（MB）"""
        raise NotImplemented

    @staticmethod
    def get_cpu_usage(deviceid, package_name: str = None):
        """获取CPU使用（MB）"""
        raise NotImplemented

    @staticmethod
    def get_fps(deviceid, package_name: str = None):
        """获取帧时间戳数据"""
        raise NotImplemented


class _AndroidHelper(_Helper):
    @staticmethod
    def listDevice():
        try:
            cmd = "adb devices"
            devices_output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            devices = [line.split()[0] for line in devices_output.stdout.splitlines()[1:] if line and 'device' in line]
            return devices
        except subprocess.CalledProcessError:
            traceback.print_exc()
            return []

    @staticmethod
    def installApp(deviceid, apk):
        try:
            command = f"adb -s {deviceid} install -r {apk}"
            subprocess.run(command, shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            traceback.print_exc()
            return False

    @staticmethod
    def launchApp(deviceid, package_name):
        try:
            command = f"adb -s {deviceid} shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
            subprocess.run(command, shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            traceback.print_exc()
            return False

    @staticmethod
    def captureScreen(deviceid, file_path: str = None):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            cmd = f"adb -s {deviceid} exec-out screencap -p"
            subprocess.run(cmd, stdout=open(file_path, 'wb'))
        except subprocess.CalledProcessError:
            traceback.print_exc()

    @staticmethod
    def get_memory_usage(deviceid, package_name: str = None):
        try:
            cmd = f"adb -s {deviceid} shell dumpsys meminfo {package_name}"
            output = subprocess.check_output(cmd, shell=True).decode()
            match = re.search(r'TOTAL\s+(\d+)\s+\d+\s+\d+\s+\d+', output)
            return int(int(match.group(1)) / 1024) if match else 0
        except subprocess.CalledProcessError:
            return 0

    @staticmethod
    def get_cpu_usage(deviceid, package_name: str = None):
        try:
            cmd = f"adb -s {deviceid} shell pidof {package_name}"
            pid = subprocess.check_output(cmd, shell=True).decode()
            pid = pid.strip()
        except subprocess.CalledProcessError as e:
            return 0
        try:
            cmd = f"adb -s {deviceid} shell dumpsys cpuinfo {pid}"
            output = subprocess.check_output(cmd, shell=True).decode()
            match = re.search(r'(\d+)%.*TOTAL', output)
            return int(match.group(1)) if match else 0
        except subprocess.CalledProcessError as e:
            print(f"Error: {str(e)}")
            return 0

    @staticmethod
    def get_fps(deviceid, package_name: str = None):
        try:
            cmd = f"adb -s {deviceid} shell dumpsys gfxinfo {package_name} reset"
            output = subprocess.check_output(cmd, shell=True).decode()
            match = re.search(r'Total frames rendered: (\d+)', output)
            return match.group(1) if match else '0'
        except subprocess.CalledProcessError as e:
            return 0


class _IOSHelper(_Helper):
    @staticmethod
    def listDevice():
        # TODO
        try:
            return usbmux.list_devices()
        except:
            # traceback.print_exc()
            return []


class DevManager:
    """
    根据device_id匹配对应的Helper
    """
    def __init__(self):
        self.android_devs = dict()
        self.ios_devs = dict()
        self._is_monitor_working = False
        self.start_monitor()
        self._dev_changed_event_listeners = []

    def start_monitor(self):
        if not self._is_monitor_working:
            print('开始设备监听')
            self._is_monitor_working = True
            t_ad_monitor = Thread(target=self.monitorAdDevices)
            t_ad_monitor.start()
            t_ios_monitor = Thread(target=self.monitorIOSDevices)
            t_ios_monitor.start()

    def stopMonitor(self):
        print('停止设备监听')
        self._is_monitor_working = False

    def monitorAdDevices(self):
        # 安卓设备
        last_devices = set()
        while self._is_monitor_working:
            devices = set(_AndroidHelper.listDevice())

            added_devices = devices - last_devices
            removed_devices = last_devices - devices
            changed = added_devices or removed_devices

            if added_devices:
                print(f"新增设备: {', '.join(added_devices)}")
                for device in added_devices:
                    brand = subprocess.run(['adb', '-s', device, 'shell', 'getprop', 'ro.product.brand'], stdout=subprocess.PIPE, text=True).stdout.strip()
                    name = subprocess.run(['adb', '-s', device, 'shell', 'getprop', 'ro.product.name'], stdout=subprocess.PIPE, text=True).stdout.strip()
                    self.android_devs[device] = {'os': PLAT_ANDROID, 'device_id': device, 'brand': brand, 'name': name}
            if removed_devices:
                print(f"移除设备: {', '.join(removed_devices)}")
                for device in removed_devices:
                    del(self.android_devs[device])

            last_devices = devices
            if changed:
                for callback in self._dev_changed_event_listeners: callback(self)
            time.sleep(0.5)

    def monitorIOSDevices(self):
        # ios设备
        last_devices = set()
        while self._is_monitor_working:
            devices = set(_IOSHelper.listDevice())

            added_devices = devices - last_devices
            removed_devices = last_devices - devices
            changed = added_devices or removed_devices

            if added_devices:
                print(f"新增设备: {', '.join(added_devices)}")
                for device in added_devices:
                    self.device_info[device] = {'os': PLAT_IOS, 'device_id': device.udid, 'brand': device.model, 'name': device.device_name}
            if removed_devices:
                print(f"移除设备: {', '.join(removed_devices)}")
                for device in removed_devices:
                    del(self.device_info[device.device_id])

            last_devices = devices
            if changed:
                for callback in self._dev_changed_event_listeners: callback(self)
            time.sleep(0.5)

    def addDevChangedEventListener(self, callback):
        self._dev_changed_event_listeners.append(callback)

    def getPlatform(self, device_id):
        return PLAT_ANDROID if device_id in self.android_devs else PLAT_IOS

    def getHelper(self, device_id):
        return _AndroidHelper if self.getPlatform(device_id) == PLAT_ANDROID else _IOSHelper

    def installApp(self, deviceid, package_name: str):
        helper = self.getHelper(deviceid)
        helper.installApp(deviceid, package_name)

    def launchApp(self, deviceid, package_name: str):
        helper = self.getHelper(deviceid)
        helper.launchApp(deviceid, package_name)

    def captureScreen(self, deviceid, file_path: str = None):
        helper = self.getHelper(deviceid)
        helper.captureScreen(deviceid, file_path)

    def clear_fps(self, deviceid, package_name):
        # 清空一次帧率数据
        helper = self.getHelper(deviceid)
        helper.get_fps(deviceid, package_name)

    def monitor_performance(self, deviceid, package_name):
        """性能监控主函数"""
        helper = self.getHelper(deviceid)
        # 获取内存数据
        mem_usage = helper.get_memory_usage(deviceid, package_name)
        # 获取CPU数据
        cpu_usage = helper.get_cpu_usage(deviceid, package_name)
        # 获取帧率数据
        fps = helper.get_fps(deviceid, package_name)
        # 获取时间
        timestamp = time.strftime("%H:%M:%S", time.localtime())

        DEBUG and print(f"{timestamp} - Memory: {mem_usage}MB, CPU: {cpu_usage}%, FPS: {fps}")
        return {
            "timestamp": timestamp,
            "memory_mb": mem_usage,
            "cpu_percent": cpu_usage,
            "fps": fps
        }

    # def __getattr__(self, item):
    #     helper = self.getHelper(item)
    #     return getattr(helper, item)


dev_mgr = DevManager()
