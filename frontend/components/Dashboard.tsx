"use client";

import { useCallback, useEffect, useState } from "react";
import { BarChart3, CalendarDays, FileStack, LayoutDashboard, LogOut, Plus, Radio, Sparkles } from "lucide-react";
import { api, ContentItem } from "@/lib/api";
import { Composer } from "./Composer";
import { PostEditor } from "./PostEditor";

type DashboardData = { status_counts: Record<string, number>; platforms: { platform: string; posts: number; views: number; engagements: number }[]; upcoming: { id: number; title: string; platform: string; scheduled_at: string }[] };

export function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [items, setItems] = useState<ContentItem[]>([]);
  const [stats, setStats] = useState<DashboardData>({ status_counts: {}, platforms: [], upcoming: [] });
  const [view, setView] = useState<"dashboard" | "create" | "library">("dashboard");
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const [content, dashboard] = await Promise.all([api<ContentItem[]>("/api/content"), api<DashboardData>("/api/dashboard")]);
    setItems(content); setStats(dashboard); setLoading(false);
  }, []);

  useEffect(() => { refresh().catch(() => onLogout()); }, [refresh, onLogout]);

  function logout() { localStorage.removeItem("omnipost_token"); onLogout(); }
  const allPosts = items.flatMap((item) => item.posts.map((post) => ({ post, title: item.title })));
  const total = Object.values(stats.status_counts).reduce((a, b) => a + b, 0);

  return (
    <main className="app-shell">
      <aside>
        <div className="brand"><span><Sparkles size={19} /></span> OmniPost</div>
        <nav>
          <button className={view === "dashboard" ? "active" : ""} onClick={() => setView("dashboard")}><LayoutDashboard size={19} /> Overview</button>
          <button className={view === "create" ? "active" : ""} onClick={() => setView("create")}><Plus size={19} /> Create</button>
          <button className={view === "library" ? "active" : ""} onClick={() => setView("library")}><FileStack size={19} /> Content library</button>
        </nav>
        <div className="demo-mode"><Radio size={17} /><div><b>Demo connectors</b><span>Safe simulated publishing</span></div></div>
        <button className="logout" onClick={logout}><LogOut size={18} /> Sign out</button>
      </aside>
      <section className="workspace">
        <header><div><p className="eyebrow">CREATOR COMMAND CENTER</p><h1>{view === "dashboard" ? "Publishing overview" : view === "create" ? "Create once, adapt everywhere" : "Content library"}</h1></div><button className="primary" onClick={() => setView("create")}><Plus size={18} /> New content</button></header>
        {loading ? <div className="loading">Loading your workspace...</div> : view === "create" ? <Composer onCreated={() => { refresh(); setView("library"); }} /> : view === "dashboard" ? <>
          <section className="metrics">
            <div><span><FileStack size={20} /></span><p>All posts</p><strong>{total}</strong><small>Across {items.length} content items</small></div>
            <div><span><CalendarDays size={20} /></span><p>Scheduled</p><strong>{stats.status_counts.scheduled ?? 0}</strong><small>Ready for the worker</small></div>
            <div><span><BarChart3 size={20} /></span><p>Published</p><strong>{stats.status_counts.published ?? 0}</strong><small>Using demo connectors</small></div>
          </section>
          <section className="overview-grid">
            <div className="section-block"><div className="section-title"><div><p className="eyebrow">RECENT WORK</p><h2>Latest adaptations</h2></div><button className="text-button" onClick={() => setView("library")}>View library</button></div>{allPosts.slice(0, 4).length ? <div className="activity-list">{allPosts.slice(0, 4).map(({post, title}) => <div key={post.id}><span className={`dot ${post.platform}`} /><div><b>{title}</b><small>{post.platform} · {post.status}</small></div><time>{new Date(items.find(i => i.posts.some(p => p.id === post.id))?.created_at ?? "").toLocaleDateString()}</time></div>)}</div> : <Empty onCreate={() => setView("create")} />}</div>
            <div className="section-block"><div className="section-title"><div><p className="eyebrow">QUEUE</p><h2>Upcoming posts</h2></div></div>{stats.upcoming.length ? <div className="activity-list">{stats.upcoming.map(post => <div key={post.id}><span className={`dot ${post.platform}`} /><div><b>{post.title}</b><small>{post.platform}</small></div><time>{new Date(post.scheduled_at).toLocaleDateString()}</time></div>)}</div> : <p className="empty-queue">No scheduled posts yet. Choose a date from the content library.</p>}</div>
          </section>
        </> : <section className="library"><div className="library-heading"><div><p className="eyebrow">ADAPTATIONS</p><h2>{allPosts.length} platform-ready posts</h2></div></div>{allPosts.length ? <div className="post-grid">{allPosts.map(({post, title}) => <PostEditor key={post.id} post={post} title={title} onChange={refresh} />)}</div> : <Empty onCreate={() => setView("create")} />}</section>}
      </section>
    </main>
  );
}

function Empty({ onCreate }: { onCreate: () => void }) {
  return <div className="empty"><Sparkles size={28} /><b>Your first post starts here</b><p>Add a title and transcript to generate tailored captions.</p><button className="primary small" onClick={onCreate}>Create content</button></div>;
}

