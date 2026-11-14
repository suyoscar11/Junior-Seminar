"use client";

import { FormEvent, useState } from "react";
import { Check, FileVideo, LoaderCircle, Sparkles, Upload } from "lucide-react";
import { api, ContentItem, Platform } from "@/lib/api";
import { PlatformIcon } from "./PlatformIcon";

export function Composer({ onCreated }: { onCreated: (item: ContentItem) => void }) {
  const [platforms, setPlatforms] = useState<Platform[]>(["instagram", "tiktok", "x"]);
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  function toggle(platform: Platform) {
    setPlatforms((current) => current.includes(platform) ? current.filter((p) => p !== platform) : [...current, platform]);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!platforms.length) return setError("Select at least one platform.");
    setBusy(true);
    setError("");
    const form = new FormData(event.currentTarget);
    try {
      let mediaId: number | null = null;
      if (file) {
        const upload = new FormData();
        upload.append("file", file);
        const media = await api<{ id: number }>("/api/media", { method: "POST", body: upload });
        mediaId = media.id;
      }
      const item = await api<ContentItem>("/api/content", {
        method: "POST",
        body: JSON.stringify({
          title: form.get("title"),
          source_notes: form.get("notes"),
          media_id: mediaId,
          platforms,
        }),
      });
      onCreated(item);
      event.currentTarget.reset();
      setFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create content");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="composer" onSubmit={submit}>
      <div className="composer-heading">
        <div><p className="eyebrow">NEW CONTENT</p><h2>Prepare a cross-platform post</h2></div>
        <span className="ai-note"><Sparkles size={15} /> Assisted adaptation</span>
      </div>
      <div className="composer-grid">
        <div className="upload-zone">
          <input id="media" type="file" accept="video/mp4,video/quicktime,video/webm,image/jpeg,image/png" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          <label htmlFor="media">
            {file ? <FileVideo size={34} /> : <Upload size={34} />}
            <b>{file ? file.name : "Choose your media"}</b>
            <span>{file ? `${(file.size / 1024 / 1024).toFixed(1)} MB` : "MP4, MOV, WebM, JPEG, or PNG"}</span>
          </label>
        </div>
        <div className="fields">
          <label>Post title<input name="title" placeholder="What is this content about?" maxLength={140} required /></label>
          <label>Transcript or key points<textarea name="notes" placeholder="Paste a transcript or summarize the main idea..." rows={5} required /></label>
          <div><span className="label-text">Publish to</span><div className="platform-picks">{(["instagram", "tiktok", "x"] as Platform[]).map((platform) => <button type="button" className={platforms.includes(platform) ? "selected" : ""} onClick={() => toggle(platform)} key={platform}><PlatformIcon platform={platform} />{platform === "x" ? "X" : platform[0].toUpperCase() + platform.slice(1)}{platforms.includes(platform) && <Check size={14} />}</button>)}</div></div>
        </div>
      </div>
      {error && <p className="form-error">{error}</p>}
      <div className="composer-actions"><p>Each caption follows the platform&apos;s tone and character limit.</p><button className="primary" disabled={busy}>{busy ? <LoaderCircle className="spin" size={18} /> : <Sparkles size={18} />}{busy ? "Preparing posts" : "Generate adaptations"}</button></div>
    </form>
  );
}

