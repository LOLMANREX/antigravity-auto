#define UNICODE
#define _UNICODE
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shlobj.h>
#include <objbase.h>
#include <shellapi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void EnsureDirectory(const wchar_t *path) {
    CreateDirectoryW(path, NULL);
}

static void CreateBatchFile(const wchar_t *filePath, const char *content) {
    HANDLE hFile = CreateFileW(filePath, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile != INVALID_HANDLE_VALUE) {
        DWORD written = 0;
        WriteFile(hFile, content, (DWORD)strlen(content), &written, NULL);
        CloseHandle(hFile);
    }
}

static void CopyLocalFile(const wchar_t *srcDir, const wchar_t *destDir, const wchar_t *filename) {
    wchar_t srcPath[MAX_PATH];
    wchar_t destPath[MAX_PATH];
    swprintf(srcPath, MAX_PATH, L"%s\\%s", srcDir, filename);
    swprintf(destPath, MAX_PATH, L"%s\\%s", destDir, filename);
    CopyFileW(srcPath, destPath, FALSE);
}

static BOOL AddToUserPath(const wchar_t *newDir) {
    HKEY hKey;
    if (RegOpenKeyExW(HKEY_CURRENT_USER, L"Environment", 0, KEY_READ | KEY_WRITE, &hKey) != ERROR_SUCCESS) {
        return FALSE;
    }

    wchar_t currentPath[32768] = {0};
    DWORD pathLen = sizeof(currentPath);
    DWORD type = REG_EXPAND_SZ;

    if (RegQueryValueExW(hKey, L"Path", NULL, &type, (LPBYTE)currentPath, &pathLen) != ERROR_SUCCESS) {
        currentPath[0] = L'\0';
    }

    // Check if newDir is already in currentPath
    if (wcsstr(currentPath, newDir) == NULL) {
        wchar_t updatedPath[32768] = {0};
        if (wcslen(currentPath) > 0) {
            swprintf(updatedPath, 32768, L"%s;%s", currentPath, newDir);
        } else {
            swprintf(updatedPath, 32768, L"%s", newDir);
        }

        RegSetValueExW(hKey, L"Path", 0, REG_EXPAND_SZ, (const BYTE*)updatedPath, (DWORD)((wcslen(updatedPath) + 1) * sizeof(wchar_t)));
        RegCloseKey(hKey);

        // Broadcast environment change to Windows Explorer and apps
        DWORD_PTR dwResult;
        SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, (LPARAM)L"Environment", SMTO_ABORTIFHUNG, 5000, &dwResult);
        return TRUE;
    }

    RegCloseKey(hKey);
    return TRUE;
}

static void ConfigureSettingsJson(const wchar_t *userProfile) {
    wchar_t dirPath[MAX_PATH];
    wchar_t filePath[MAX_PATH];
    swprintf(dirPath, MAX_PATH, L"%s\\.gemini", userProfile);
    CreateDirectoryW(dirPath, NULL);
    swprintf(dirPath, MAX_PATH, L"%s\\.gemini\\antigravity-cli", userProfile);
    CreateDirectoryW(dirPath, NULL);
    swprintf(filePath, MAX_PATH, L"%s\\.gemini\\antigravity-cli\\settings.json", userProfile);

    // Convert userProfile to JSON-escaped UTF-8 string
    char userProfileA[MAX_PATH];
    WideCharToMultiByte(CP_UTF8, 0, userProfile, -1, userProfileA, MAX_PATH, NULL, NULL);

    char escapedProfile[MAX_PATH * 2] = {0};
    int j = 0;
    for (int i = 0; userProfileA[i] != '\0' && j < (MAX_PATH * 2 - 2); i++) {
        if (userProfileA[i] == '\\') {
            escapedProfile[j++] = '\\';
            escapedProfile[j++] = '\\';
        } else {
            escapedProfile[j++] = userProfileA[i];
        }
    }
    escapedProfile[j] = '\0';

    char jsonContent[4096];
    snprintf(jsonContent, sizeof(jsonContent),
        "{\n"
        "  \"artifactReviewPolicy\": \"always-proceed\",\n"
        "  \"toolPermission\": \"always-proceed\",\n"
        "  \"trustedWorkspaces\": [\n"
        "    \"%s\"\n"
        "  ]\n"
        "}\n",
        escapedProfile
    );

    HANDLE hFile = CreateFileW(filePath, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile != INVALID_HANDLE_VALUE) {
        DWORD written = 0;
        WriteFile(hFile, jsonContent, (DWORD)strlen(jsonContent), &written, NULL);
        CloseHandle(hFile);
    }
}

static void CreateDesktopShortcut(const wchar_t *userProfile, const wchar_t *targetBin, const wchar_t *shortcutName, const wchar_t *args) {
    HRESULT hr = CoInitialize(NULL);
    if (FAILED(hr)) return;

    IShellLinkW* psl = NULL;
    hr = CoCreateInstance(&CLSID_ShellLink, NULL, CLSCTX_INPROC_SERVER, &IID_IShellLinkW, (LPVOID*)&psl);
    if (SUCCEEDED(hr)) {
        psl->lpVtbl->SetPath(psl, targetBin);
        if (args && wcslen(args) > 0) {
            psl->lpVtbl->SetArguments(psl, args);
        }

        IPersistFile* ppf = NULL;
        hr = psl->lpVtbl->QueryInterface(psl, &IID_IPersistFile, (LPVOID*)&ppf);
        if (SUCCEEDED(hr)) {
            wchar_t shortcutPath[MAX_PATH];
            swprintf(shortcutPath, MAX_PATH, L"%s\\Desktop\\%s.lnk", userProfile, shortcutName);
            ppf->lpVtbl->Save(ppf, shortcutPath, TRUE);
            ppf->lpVtbl->Release(ppf);
        }
        psl->lpVtbl->Release(psl);
    }
    CoUninitialize();
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    int choice = MessageBoxW(
        NULL,
        L"Bienvenue dans l'installateur Antigravity Auto pour Windows !\n\n"
        L"Cette installation automatique va configurer :\n"
        L" • agy-auto et agy-yolo (Mode sans permissions requises)\n"
        L" • agy-enter (Auto-Enter en ligne de commande)\n"
        L" • La configuration persistante settings.json\n"
        L" • L'intégration au PATH Windows et des raccourcis\n\n"
        L"Souhaitez-vous lancer l'installation ?",
        L"Installation Antigravity Auto",
        MB_YESNO | MB_ICONQUESTION
    );

    if (choice != IDYES) {
        return 0;
    }

    // Récupération des dossiers Windows
    wchar_t localAppData[MAX_PATH] = {0};
    wchar_t userProfile[MAX_PATH] = {0};
    GetEnvironmentVariableW(L"LOCALAPPDATA", localAppData, MAX_PATH);
    GetEnvironmentVariableW(L"USERPROFILE", userProfile, MAX_PATH);

    if (wcslen(localAppData) == 0 || wcslen(userProfile) == 0) {
        MessageBoxW(NULL, L"Impossible de localiser les variables d'environnement Windows.", L"Erreur", MB_OK | MB_ICONERROR);
        return 1;
    }

    // Dossier d'installation des binaires : %LOCALAPPDATA%\agy\bin
    wchar_t agyDir[MAX_PATH];
    wchar_t binDir[MAX_PATH];
    wchar_t shareDir[MAX_PATH];
    swprintf(agyDir, MAX_PATH, L"%s\\agy", localAppData);
    swprintf(binDir, MAX_PATH, L"%s\\agy\\bin", localAppData);
    swprintf(shareDir, MAX_PATH, L"%s\\antigravity-auto", localAppData);

    EnsureDirectory(agyDir);
    EnsureDirectory(binDir);
    EnsureDirectory(shareDir);

    // Détection du répertoire courant de l'exécutable
    wchar_t currentExePath[MAX_PATH] = {0};
    GetModuleFileNameW(NULL, currentExePath, MAX_PATH);
    wchar_t *lastSlash = wcsrchr(currentExePath, L'\\');
    if (lastSlash) *lastSlash = L'\0';

    // Copie des scripts Python si présents à côté de Setup.exe
    CopyLocalFile(currentExePath, shareDir, L"auto_enter_cli.py");
    CopyLocalFile(currentExePath, shareDir, L"auto_enter_app.py");

    // 1. Création de agy-auto.bat
    wchar_t agyAutoBat[MAX_PATH];
    swprintf(agyAutoBat, MAX_PATH, L"%s\\agy-auto.bat", binDir);
    CreateBatchFile(agyAutoBat, "@echo off\r\nagy --dangerously-skip-permissions %*\r\n");

    // 2. Création de agy-yolo.bat
    wchar_t agyYoloBat[MAX_PATH];
    swprintf(agyYoloBat, MAX_PATH, L"%s\\agy-yolo.bat", binDir);
    CreateBatchFile(agyYoloBat, "@echo off\r\nagy --dangerously-skip-permissions %*\r\n");

    // 3. Création de agy-enter.bat
    wchar_t agyEnterBat[MAX_PATH];
    swprintf(agyEnterBat, MAX_PATH, L"%s\\agy-enter.bat", binDir);
    char enterBatContent[1024];
    char shareDirA[MAX_PATH];
    WideCharToMultiByte(CP_UTF8, 0, shareDir, -1, shareDirA, MAX_PATH, NULL, NULL);
    snprintf(enterBatContent, sizeof(enterBatContent), "@echo off\r\npython \"%s\\auto_enter_cli.py\" %%*\r\n", shareDirA);
    CreateBatchFile(agyEnterBat, enterBatContent);

    // 4. Ajout au PATH utilisateur Windows
    AddToUserPath(binDir);

    // 5. Configuration de settings.json
    ConfigureSettingsJson(userProfile);

    // 6. Création du raccourci Bureau pour lancer le CLI sans permissions
    CreateDesktopShortcut(userProfile, agyAutoBat, L"Antigravity CLI (Sans Permissions)", NULL);

    // 7. Vérification de la présence de agy.exe
    wchar_t agyExe[MAX_PATH];
    swprintf(agyExe, MAX_PATH, L"%s\\agy.exe", binDir);
    if (GetFileAttributesW(agyExe) == INVALID_FILE_ATTRIBUTES) {
        int installAgy = MessageBoxW(
            NULL,
            L"Antigravity CLI ('agy') n'a pas encore été détecté dans %LOCALAPPDATA%\\agy\\bin.\n\n"
            L"Souhaitez-vous lancer automatiquement l'installation officielle de Antigravity CLI maintenant ?",
            L"Antigravity CLI manquant",
            MB_YESNO | MB_ICONINFORMATION
        );

        if (installAgy == IDYES) {
            ShellExecuteW(
                NULL,
                L"open",
                L"powershell.exe",
                L"-NoProfile -ExecutionPolicy Bypass -Command \"irm https://antigravity.google/cli/install.ps1 | iex\"",
                NULL,
                SW_SHOWNORMAL
            );
        }
    }

    MessageBoxW(
        NULL,
        L"✨ Félicitations ! Antigravity Auto a été installé avec succès.\n\n"
        L"Vous pouvez désormais ouvrir n'importe quel terminal Windows (PowerShell, CMD, Terminal) et taper :\n"
        L"   agy-auto\n"
        L"   agy-yolo\n\n"
        L"Toutes les commandes s'exécuteront sans demande d'approbation manuelle !\n"
        L"Un raccourci a également été ajouté sur votre Bureau.",
        L"Installation terminée",
        MB_OK | MB_ICONINFORMATION
    );

    return 0;
}
