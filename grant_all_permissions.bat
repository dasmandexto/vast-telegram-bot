@echo off
chcp 65001 > nul
echo ====================================================
echo  Gesture Intent Launcher - Выдача всех прав через ADB
echo ====================================================

echo [1/8] Проверка подключения устройства...
adb devices
echo.

echo [2/8] Установка / Обновление APK со всеми runtime-правами (-g)...
adb install -r -g "GestureIntentLauncher.apk"
echo.

echo [3/8] Включение AccessibilityService напрямую через Secure Settings...
adb shell settings put secure enabled_accessibility_services com.gesture.launcher/com.gesture.launcher.service.GestureAccessibilityService
adb shell settings put secure accessibility_enabled 1
echo [OK] AccessibilityService активирован!
echo.

echo [4/8] Выдача привилегированных разрешений (pm grant)...
adb shell pm grant com.gesture.launcher android.permission.WRITE_SECURE_SETTINGS
adb shell pm grant com.gesture.launcher android.permission.PACKAGE_USAGE_STATS
adb shell pm grant com.gesture.launcher android.permission.POST_NOTIFICATIONS
adb shell pm grant com.gesture.launcher android.permission.DUMP
adb shell pm grant com.gesture.launcher android.permission.READ_LOGS
echo [OK] PM разрешения выданы!
echo.

echo [5/8] Выдача специальных операций через AppOps (Overlay, UsageStats)...
adb shell appops set com.gesture.launcher SYSTEM_ALERT_WINDOW allow
adb shell appops set com.gesture.launcher GET_USAGE_STATS allow
adb shell appops set com.gesture.launcher PROJECT_MEDIA allow
adb shell appops set com.gesture.launcher AUTO_REVOKE_PERMISSIONS_IF_UNUSED ignore
echo [OK] AppOps настроены!
echo.

echo [6/8] Добавление в белый список Doze / Игнорирование экономии батареи...
adb shell dumpsys deviceidle whitelist +com.gesture.launcher
adb shell cmd deviceidle whitelist +com.gesture.launcher
echo [OK] Энергосбережение отключено!
echo.

echo [7/8] Установка наивысшего приоритета выполнения (standby bucket: ACTIVE)...
adb shell am set-standby-bucket com.gesture.launcher active
echo.

echo [8/8] Запуск Gesture Intent Launcher...
adb shell am start -n com.gesture.launcher/.ui.MainActivity
echo.
echo ====================================================
echo  ГОТОВО! Все возможные права выданы, служба активна!
echo ====================================================
pause
