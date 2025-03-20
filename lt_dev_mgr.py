# -*- coding: utf-8 -*-
"""
@Time    : 2025/1/7 15:26
@Author  : wenjiawei
"""
import os
import subprocess
import time
import traceback
from threading import Thread

from pymobiledevice3 import usbmux

PLAT_ANDROID = 'Android'
PLAT_IOS = 'iOS'


class Helper:
    @staticmethod
    def listDevice():
        raise NotImplemented

    @staticmethod
    def launchApp(deviceid, package_name: str):
        raise NotImplemented

    @staticmethod
    def captureScreen(deviceid, file_path: str = None):
        raise NotImplemented


class AndroidHelper(Helper):
    @staticmethod
    def listDevice():
        try:
            devices_output = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            devices = [line.split()[0] for line in devices_output.stdout.splitlines()[1:] if line and 'device' in line]
            return devices
        except:
            traceback.print_exc()
            return []

    @staticmethod
    def launchApp(deviceid, package_name):
        command = f"adb -s {deviceid} shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
        subprocess.run(command, shell=True, check=True)
        return True

    @staticmethod
    def captureScreen(deviceid, file_path: str = None):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        subprocess.run(['adb', 'exec-out', 'screencap', '-p'], stdout=open(file_path, 'wb'))


class IOSHelper(Helper):
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
            print('设备监听')
            self._is_monitor_working = True
            t_ad_monitor = Thread(target=self.monitorAdDevices)
            t_ad_monitor.start()
            t_ios_monitor = Thread(target=self.monitorIOSDevices)
            t_ios_monitor.start()

    def stopMonitor(self, widget, event):
        self._is_monitor_working = False

    def monitorAdDevices(self):
        # 安卓设备
        last_devices = set()
        while self._is_monitor_working:
            devices = set(AndroidHelper.listDevice())

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
            devices = set(IOSHelper.listDevice())

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
        return AndroidHelper if self.getPlatform(device_id) == PLAT_ANDROID else IOSHelper

    def launchApp(self, deviceid, package_name: str):
        helper = self.getHelper(deviceid)
        helper.launchApp(deviceid, package_name)

    def captureScreen(self, deviceid, file_path: str = None):
        helper = self.getHelper(deviceid)
        helper.captureScreen(deviceid, file_path)

    # def __getattr__(self, item):
    #     helper = self.getHelper(item)
    #     return getattr(helper, item)


dev_mgr = DevManager()
