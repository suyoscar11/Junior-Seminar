"use client";

import { useState } from "react";
import { CalendarClock, CheckCircle2, Pencil, Send, X } from "lucide-react";
import { api, Post } from "@/lib/api";
import { PlatformIcon } from "./PlatformIcon";

export function PostEditor({ post, title, onChange }: { post: Post; title: string; onChange: () => void }) {
  const [editing, setEditing] = useState(false);
  const [caption, setCaption] = useState(post.caption);
  const [hashtags, setHashtags] = useState(post.hashtags);
  const [schedule, setSchedule] = useState("");
  const [busy, setBusy] = useState(false);

  async function save() {
    setBusy(true);
    await api(`/api/posts/${post.id}`, { method: "PATCH", body: JSON.stringify({ caption, hashtags }) });
    setEditing(false); setBusy(false); onChange();
  }

  async function publish() {
    setBusy(true); await api(`/api/posts/${post.id}/publish`, { method: "POST" }); setBusy(false); onChange();
  }

  async function schedulePost() {
    if (!schedule) return;
    setBusy(true);
    await api(`/api/posts/${post.id}/schedule`, { method: "POST", body: JSON.stringify({ scheduled_at: new Date(schedule).toISOString() }) });
    setBusy(false); onChange();
  }

  return (
    <article className="post-card">
      <div className="post-top"><span className={`platform-mark ${post.platform}`}><PlatformIcon platform={post.platform} /></span><div><b>{post.platform === "x" ? "X" : post.platform[0].toUpperCase() + post.platform.slice(1)}</b><small>{title}</small></div><span className={`status ${post.status}`}>{post.status}</span></div>
      {editing ? <div className="edit-fields"><textarea value={caption} onChange={(e) => setCaption(e.target.value)} rows={7} /><input value={hashtags} onChange={(e) => setHashtags(e.target.value)} /><div><button onClick={() => setEditing(false)}><X size={15} /> Cancel</button><button className="primary small" onClick={save} disabled={busy}>Save</button></div></div> : <><p className="caption">{post.caption}</p><p className="hashtags">{post.hashtags}</p></>}
      {post.scheduled_at && <p className="schedule-line"><CalendarClock size={15} /> {new Date(post.scheduled_at).toLocaleString()}</p>}
      {post.external_id && <p className="schedule-line"><CheckCircle2 size={15} /> Demo ID: {post.external_id}</p>}
      {!editing && <div className="post-actions"><button onClick={() => setEditing(true)}><Pencil size={15} /> Edit</button><div className="schedule-control"><input type="datetime-local" value={schedule} onChange={(e) => setSchedule(e.target.value)} /><button onClick={schedulePost} disabled={!schedule || busy}><CalendarClock size={15} /> Schedule</button></div><button className="primary small" onClick={publish} disabled={busy || post.status === "published"}><Send size={15} /> {post.status === "published" ? "Published" : "Publish"}</button></div>}
    </article>
  );
}

