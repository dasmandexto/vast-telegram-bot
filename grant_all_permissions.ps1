# ====================================================
#  Gesture Intent Launcher - Выдача всех прав через ADB
# ====================================================

Write-Host "[1/8] Проверка подключения устройства..." -ForegroundColor Cyan
adb devices

Write-Host "`n[2/8] Установка / Обновление APK со всеми runtime-правами (-g)..." -ForegroundColor Cyan
adb install -r -g "GestureIntentLauncher.apk"

Write-Host "`n[3/8] Включение AccessibilityService напрямую через Secure Settings..." -ForegroundColor Cyan
adb shell settings put secure enabled_accessibility_services com.gesture.launcher/com.gesture.launcher.service.GestureAccessibilityService
adb shell settings put secure accessibility_enabled 1
Write-Host "[OK] AccessibilityService активирован!" -ForegroundColor Green

Write-Host "`n[4/8] Выдача привилегированных разрешений (pm grant)..." -ForegroundColor Cyan
adb shell pm grant com.gesture.launcher android.permission.WRITE_SECURE_SETTINGS
adb shell pm grant com.gesture.launcher android.permission.PACKAGE_USAGE_STATS
adb shell pm grant com.gesture.launcher android.permission.POST_NOTIFICATIONS
adb shell pm grant com.gesture.launcher android.permission.DUMP
adb shell pm grant com.gesture.launcher android.permission.READ_LOGS
Write-Host "[OK] PM разрешения выданы!" -ForegroundColor Green

Write-Host "`n[5/8] Выдача специальных операций через AppOps (Overlay, UsageStats)..." -ForegroundColor Cyan
adb shell appops set com.gesture.launcher SYSTEM_ALERT_WINDOW allow
adb shell appops set com.gesture.launcher GET_USAGE_STATS allow
adb shell appops set com.gesture.launcher PROJECT_MEDIA allow
adb shell appops set com.gesture.launcher AUTO_REVOKE_PERMISSIONS_IF_UNUSED ignore
Write-Host "[OK] AppOps настроены!" -ForegroundColor Green

Write-Host "`n[6/8] Добавление в белый список Doze / Игнорирование экономии батареи..." -ForegroundColor Cyan
adb shell dumpsys deviceidle whitelist +com.gesture.launcher
adb shell cmd deviceidle whitelist +com.gesture.launcher
Write-Host "[OK] Энергосбережение отключено!" -ForegroundColor Green

Write-Host "`n[7/8] Установка наивысшего приоритета выполнения (standby bucket: ACTIVE)..." -ForegroundColor Cyan
adb shell am set-standby-bucket com.gesture.launcher active

Write-Host "`n[8/8] Запуск Gesture Intent Launcher..." -ForegroundColor Cyan
adb shell am start -n com.gesture.launcher/.ui.MainActivity

Write-Host "`n====================================================" -ForegroundColor Green
Write-Host " ГОТОВО! Все возможные права выданы, служба активна!" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
