"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import {
  ChevronDown,
  ChevronRight,
  FileText,
  Layers,
  MessageSquarePlus,
  PanelLeftClose,
  PanelLeftOpen,
  Settings,
  X,
} from "lucide-react";
import { useState } from "react";

import { useSidebar } from "@/components/layout/sidebar-context";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { useChats, useCreateChat } from "@/hooks/use-chats";
import { setLastChatId } from "@/lib/chat-storage";
import { knowledgeNavigation, routes } from "@/lib/routes";
import { backdropVariants, sidebarTransition, transitionFast } from "@/lib/motion";
import { cn } from "@/lib/utils";

const SIDEBAR_WIDTH_EXPANDED = 260;
const SIDEBAR_WIDTH_COLLAPSED = 68;

function ChatHistory({
  collapsed,
  onNavigate,
}: {
  collapsed: boolean;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const { data, isLoading } = useChats();

  if (collapsed) {
    return null;
  }

  return (
    <div className="px-2">
      <p className="mb-2 px-2.5 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
        Chat history
      </p>
      {isLoading ? (
        <div className="space-y-2 px-2">
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-8 w-full" />
        </div>
      ) : data?.items.length ? (
        <div className="space-y-0.5">
          {data.items.map((chat) => {
            const href = `${routes.chat}/${chat.id}`;
            const isActive = pathname === href;
            return (
              <Link
                key={chat.id}
                href={href}
                onClick={onNavigate}
                className={cn(
                  "block truncate rounded-lg px-2.5 py-2 text-sm transition-colors",
                  isActive
                    ? "bg-primary/15 text-primary"
                    : "text-text-secondary hover:bg-sidebar-accent hover:text-foreground",
                )}
                title={chat.title}
              >
                {chat.title}
              </Link>
            );
          })}
        </div>
      ) : (
        <p className="px-2.5 text-sm text-text-secondary">No chats yet</p>
      )}
    </div>
  );
}

function KnowledgeNav({
  collapsed,
  onNavigate,
}: {
  collapsed: boolean;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const [open, setOpen] = useState(true);

  if (collapsed) {
    return (
      <nav className="space-y-0.5 px-2" aria-label="Knowledge">
        {knowledgeNavigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              title={item.name}
              className={cn(
                "flex items-center justify-center rounded-lg px-2 py-2 text-sm",
                isActive
                  ? "bg-primary/15 text-primary"
                  : "text-text-secondary hover:bg-sidebar-accent",
              )}
            >
              {item.name === "Documents" ? (
                <FileText className="size-4" />
              ) : (
                <Layers className="size-4" />
              )}
            </Link>
          );
        })}
      </nav>
    );
  }

  return (
    <div className="px-2">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="mb-2 flex w-full items-center justify-between px-2.5 text-[11px] font-medium uppercase tracking-wider text-muted-foreground"
        aria-expanded={open}
      >
        Knowledge
        {open ? <ChevronDown className="size-3.5" /> : <ChevronRight className="size-3.5" />}
      </button>
      {open ? (
        <nav className="space-y-0.5" aria-label="Knowledge">
          {knowledgeNavigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onNavigate}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-2.5 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary/15 text-primary"
                    : "text-text-secondary hover:bg-sidebar-accent hover:text-foreground",
                )}
              >
                {item.name === "Documents" ? (
                  <FileText className="size-4 shrink-0" />
                ) : (
                  <Layers className="size-4 shrink-0" />
                )}
                {item.name}
              </Link>
            );
          })}
        </nav>
      ) : null}
    </div>
  );
}

function SidebarContent({
  collapsed,
  onNavigate,
  showCollapseToggle = true,
}: {
  collapsed: boolean;
  onNavigate?: () => void;
  showCollapseToggle?: boolean;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { toggleCollapsed } = useSidebar();
  const createChat = useCreateChat();

  async function handleNewChat() {
    const chat = await createChat.mutateAsync(undefined);
    setLastChatId(chat.id);
    onNavigate?.();
    router.push(`${routes.chat}/${chat.id}`);
  }

  return (
    <>
      <div
        className={cn(
          "flex h-14 shrink-0 items-center border-b border-sidebar-border sm:h-16",
          collapsed ? "justify-center px-2" : "justify-between px-3",
        )}
      >
        {!collapsed ? (
          <Link href={routes.chat} className="flex items-center gap-2.5 px-1">
            <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-xs font-bold text-primary-foreground">
              AI
            </span>
            <span className="text-sm font-semibold tracking-tight">Knowledge</span>
          </Link>
        ) : (
          <Link
            href={routes.chat}
            className="flex size-8 items-center justify-center rounded-lg bg-primary text-xs font-bold text-primary-foreground"
            aria-label="Home"
          >
            AI
          </Link>
        )}
        {showCollapseToggle ? (
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={toggleCollapsed}
            className={cn("text-text-secondary", collapsed && "hidden md:inline-flex")}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? (
              <PanelLeftOpen className="size-4" />
            ) : (
              <PanelLeftClose className="size-4" />
            )}
          </Button>
        ) : null}
      </div>

      <div className="space-y-3 border-b border-sidebar-border px-2 py-3">
        <Button
          type="button"
          className={cn("w-full", collapsed && "px-0")}
          size={collapsed ? "icon-sm" : "sm"}
          onClick={() => void handleNewChat()}
          disabled={createChat.isPending}
          aria-label="New chat"
        >
          <MessageSquarePlus className="size-4" />
          {!collapsed ? "New chat" : null}
        </Button>
      </div>

      <ScrollArea className="flex-1 py-3">
        <div className="space-y-4">
          <ChatHistory collapsed={collapsed} onNavigate={onNavigate} />
          <KnowledgeNav collapsed={collapsed} onNavigate={onNavigate} />
        </div>
      </ScrollArea>

      <div className="border-t border-sidebar-border p-2">
        <Link
          href={routes.settings}
          onClick={onNavigate}
          title="Settings"
          className={cn(
            "flex items-center gap-3 rounded-lg px-2.5 py-2 text-sm font-medium transition-colors",
            collapsed && "justify-center px-2",
            pathname.startsWith(routes.settings)
              ? "bg-primary/15 text-primary"
              : "text-text-secondary hover:bg-sidebar-accent hover:text-foreground",
          )}
        >
          <Settings className="size-4 shrink-0" />
          {!collapsed ? "Settings" : null}
        </Link>
      </div>
    </>
  );
}

export function Sidebar() {
  const { isCollapsed, isMobile, isMobileOpen, setMobileOpen } = useSidebar();

  if (isMobile) {
    return (
      <AnimatePresence>
        {isMobileOpen ? (
          <>
            <motion.div
              key="sidebar-backdrop"
              initial="initial"
              animate="animate"
              exit="exit"
              variants={backdropVariants}
              transition={transitionFast}
              className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm"
              onClick={() => setMobileOpen(false)}
            />
            <motion.aside
              key="sidebar-drawer"
              initial={{ x: -SIDEBAR_WIDTH_EXPANDED }}
              animate={{ x: 0 }}
              exit={{ x: -SIDEBAR_WIDTH_EXPANDED }}
              transition={sidebarTransition}
              className="fixed inset-y-0 left-0 z-50 flex w-[260px] flex-col border-r border-sidebar-border bg-sidebar"
            >
              <div className="absolute right-2 top-3">
                <Button
                  variant="ghost"
                  size="icon-sm"
                  onClick={() => setMobileOpen(false)}
                  aria-label="Close sidebar"
                >
                  <X className="size-4" />
                </Button>
              </div>
              <SidebarContent
                collapsed={false}
                onNavigate={() => setMobileOpen(false)}
                showCollapseToggle={false}
              />
            </motion.aside>
          </>
        ) : null}
      </AnimatePresence>
    );
  }

  return (
    <motion.aside
      initial={false}
      animate={{
        width: isCollapsed ? SIDEBAR_WIDTH_COLLAPSED : SIDEBAR_WIDTH_EXPANDED,
      }}
      transition={sidebarTransition}
      className="hidden h-screen shrink-0 flex-col overflow-hidden border-r border-sidebar-border bg-sidebar md:flex"
    >
      <SidebarContent collapsed={isCollapsed} />
    </motion.aside>
  );
}
