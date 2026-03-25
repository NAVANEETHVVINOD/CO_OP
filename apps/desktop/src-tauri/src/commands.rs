use tauri::{AppHandle, Runtime};
use tauri_plugin_shell::ShellExt;
use serde::Serialize;

#[derive(Serialize)]
pub struct SystemStatus {
    pub healthy: bool,
    pub message: String,
}

#[tauri::command]
pub async fn get_system_status<R: Runtime>(app: AppHandle<R>) -> Result<String, String> {
    run_coop_cmd(&app, vec!["gateway", "status", "--json"]).await
}

#[tauri::command]
pub async fn start_gateway<R: Runtime>(app: AppHandle<R>) -> Result<String, String> {
    run_coop_cmd(&app, vec!["gateway", "start"]).await
}

#[tauri::command]
pub async fn stop_gateway<R: Runtime>(app: AppHandle<R>) -> Result<String, String> {
    run_coop_cmd(&app, vec!["gateway", "stop"]).await
}

pub async fn run_coop_cmd<R: Runtime>(app: &AppHandle<R>, args: Vec<&str>) -> Result<String, String> {
    let output = app.shell()
        .command("coop")
        .args(args)
        .output()
        .await
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

#[tauri::command]
pub async fn open_logs<R: Runtime>(app: AppHandle<R>) -> Result<(), String> {
    let mut log_path = dirs::home_dir().ok_or("Could not find home directory")?;
    log_path.push(".co-op");
    log_path.push("logs");
    log_path.push("coop.log");

    if !log_path.exists() {
        return Err("Log file does not exist yet.".to_string());
    }

    // Open with default system app
    #[cfg(target_os = "windows")]
    {
        app.shell()
            .command("cmd")
            .args(["/C", "start", "", log_path.to_str().unwrap()])
            .spawn()
            .map_err(|e| e.to_string())?;
    }
    #[cfg(not(target_os = "windows"))]
    {
        app.shell()
            .command("open")
            .args([log_path.to_str().unwrap()])
            .spawn()
            .map_err(|e| e.to_string())?;
    }

    Ok(())
}
