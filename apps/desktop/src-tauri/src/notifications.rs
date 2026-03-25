use tauri::{AppHandle, Manager, Runtime};
use tauri_plugin_notification::NotificationExt;
use std::time::Duration;
use serde::Deserialize;

#[derive(Deserialize)]
struct Approval {
    id: String,
    description: String,
}

pub fn start_polling<R: Runtime>(app: AppHandle<R>) {
    tauri::async_runtime::spawn(async move {
        let mut interval = tokio::time::interval(Duration::from_secs(30));
        loop {
            interval.tick().await;
            if let Ok(approvals) = fetch_pending_approvals().await {
                if !approvals.is_empty() {
                    let _ = app.notification()
                        .builder()
                        .title("Pending Approvals")
                        .body(format!("You have {} actions waiting for approval.", approvals.len()))
                        .show();
                }
            }
        }
    });
}

async fn fetch_pending_approvals() -> Result<Vec<Approval>, reqwest::Error> {
    let client = reqwest::Client::new();
    let res = client.get("http://localhost:8000/v1/approvals")
        .send()
        .await?
        .json::<Vec<Approval>>()
        .await?;
    Ok(res)
}
