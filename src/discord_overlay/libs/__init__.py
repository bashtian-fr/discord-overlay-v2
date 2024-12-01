from pyqttoast import Toast, ToastPreset


def show_toast(parent, title, text, duration=5000, preset=None, icon=None):
    toast = Toast(parent)
    toast.setDuration(duration)
    toast.setTitle(title)
    toast.setText(text)

    if preset == "error":
        preset = ToastPreset.ERROR

    if preset == "success":
        preset = ToastPreset.SUCCESS

    if preset:
        toast.applyPreset(preset)

    if icon:
        toast.setIconColor(None)
        toast.setShowIcon(True)
        toast.setIcon(icon)

    toast.setShowDurationBar(True)
    toast.show()
