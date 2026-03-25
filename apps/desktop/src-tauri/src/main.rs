mod tray;
mod notifications;
mod commands;

use tauri::{Manager, WebviewWindowBuilder, WebviewUrl};

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_autostart::init(tauri_plugin_autostart::MacosLauncher::LaunchAgent, Some(vec!["--hidden"])))
        .setup(|app| {
            // Start the gateway in the background
            let app_handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                let _ = commands::run_coop_cmd(&app_handle, vec!["gateway", "start"]).await;
            });

            // Start notification polling
            notifications::start_polling(app.handle().clone());
            
            Ok(())
        })
        .menu(tauri::menu::Menu::default(app.handle())?)
        .setup(|app| {
            tray::setup_tray(app.handle())?;
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::get_system_status,
            commands::start_gateway,
            commands::stop_gateway
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
