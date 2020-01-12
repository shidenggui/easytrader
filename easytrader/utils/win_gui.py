# coding:utf-8
import win32gui


def SetForegroundWindow(hwd):
    win32gui.SetForegroundWindow(hwd._as_parameter_)


def ShowWindow(hwd, window_status):
    win32gui.ShowWindow(hwd._as_parameter_, window_status)
