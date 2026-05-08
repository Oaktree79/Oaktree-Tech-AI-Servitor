import * as vscode from "vscode";
import { execFile } from "node:child_process";

function runServiter(args: string[], cwd: string): Promise<string> {
  return new Promise((resolve, reject) => {
    execFile("serviter", args, { cwd }, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(stderr || error.message));
      } else {
        resolve(stdout);
      }
    });
  });
}

export function activate(context: vscode.ExtensionContext) {
  const analyze = vscode.commands.registerCommand("aiServiter.analyze", async () => {
    const folder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!folder) {
      vscode.window.showErrorMessage("Open a workspace folder first.");
      return;
    }

    try {
      const output = await runServiter([folder, "analyze"], folder);
      const doc = await vscode.workspace.openTextDocument({
        language: "json",
        content: output,
      });
      await vscode.window.showTextDocument(doc);
    } catch (err: any) {
      vscode.window.showErrorMessage(`AI Serviter analyze failed: ${err.message}`);
    }
  });

  const plan = vscode.commands.registerCommand("aiServiter.plan", async () => {
    const folder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!folder) {
      vscode.window.showErrorMessage("Open a workspace folder first.");
      return;
    }

    const request = await vscode.window.showInputBox({
      prompt: "Describe the coding task",
      placeHolder: "Example: add plugin module tests",
    });
    if (!request) return;

    try {
      const output = await runServiter([folder, "plan", request], folder);
      const doc = await vscode.workspace.openTextDocument({
        language: "json",
        content: output,
      });
      await vscode.window.showTextDocument(doc);
    } catch (err: any) {
      vscode.window.showErrorMessage(`AI Serviter plan failed: ${err.message}`);
    }
  });

  context.subscriptions.push(analyze, plan);
}

export function deactivate() {}
