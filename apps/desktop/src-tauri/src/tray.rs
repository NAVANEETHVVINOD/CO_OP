use tauri::{
    menu::{Menu, MenuItem},
    tray::{TrayIconBuilder, TrayIconEvent},
    AppHandle, Manager, Runtime,
};

pub fn setup_tray<R: Runtime>(app: &AppHandle<R>) -> tauri::Result<()> {
    let quit_i = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
    let show_i = MenuItem::with_id(app, "show", "Open Dashboard", true, None::<&str>)?;
    let start_i = MenuItem::with_id(app, "start", "Start Gateway", true, None::<&str>)?;
    let stop_i = MenuItem::with_id(app, "stop", "Stop Gateway", true, None::<&str>)?;
    let logs_i = MenuItem::with_id(app, "logs", "View Logs", true, None::<&str>)?;

    let menu = Menu::with_items(app, &[&show_i, &start_i, &stop_i, &logs_i, &quit_i])?;

    let _ = TrayIconBuilder::with_id("main")
        .menu(&menu)
        .show_menu_on_left_click(true)
        .on_menu_event(|app, event| match event.id.as_ref() {
            "quit" => {
                app.exit(0);
            }
            "show" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
            "start" => {
                let app_handle = app.clone();
                tauri::async_runtime::spawn(async move {
                    let _ = crate::commands::start_gateway(app_handle).await;
                });
            }
            "stop" => {
                let app_handle = app.clone();
                tauri::async_runtime::spawn(async move {
                    let _ = crate::commands::stop_gateway(app_handle).await;
                });
            }
            "logs" => {
                let app_handle = app.clone();
                tauri::async_runtime::spawn(async move {
                    let _ = crate::commands::open_logs(app_handle).await;
                });
            }
            _ => (),
        })
        .build(app)?;

    Ok(())
}
