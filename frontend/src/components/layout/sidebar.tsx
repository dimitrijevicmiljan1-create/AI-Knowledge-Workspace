"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import {
  BookMarked,
  FolderGit2,
  LayoutDashboard,
  MessageSquare,
  PanelLeftClose,
  PanelLeftOpen,
  Settings,
  Layers,
  X,
} from "lucide-react";

import { useSidebar } from "@/components/layout/sidebar-context";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { appNavigation, routes } from "@/lib/routes";
import { backdropVariants, sidebarTransition, transitionFast } from "@/lib/motion";
import { cn } from "@/lib/utils";

const iconMap = {
  [routes.dashboard]: LayoutDashboard,
  [routes.chat]: MessageSquare,
  [routes.sources]: Layers,
  [routes.github]: FolderGit2,
  [routes.obsidian]: BookMarked,
  [routes.settings]: Settings,
};

const SIDEBAR_WIDTH_EXPANDED = 260;
const SIDEBAR_WIDTH_COLLAPSED = 68;

function SidebarNav({
  collapsed,
  onNavigate,
}: {
  collapsed: boolean;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-0.5 px-2" aria-label="Application">
      {!collapsed ? (
        <p className="mb-2 px-2.5 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
          Workspace
        </p>
      ) : null}
      {appNavigation.map((item) => {
        const isActive =
          pathname === item.href || pathname.startsWith(`${item.href}/`);
        const Icon = iconMap[item.href];

        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            title={collapsed ? item.name : undefined}
            className={cn(
              "group flex items-center gap-3 rounded-lg px-2.5 py-2 text-sm font-medium transition-all duration-200",
              collapsed && "justify-center px-2",
              isActive
                ? "bg-primary/15 text-primary shadow-[inset_0_0_0_1px_rgba(139,92,246,0.25)]"
                : "text-text-secondary hover:bg-sidebar-accent hover:text-foreground",
            )}
          >
            <Icon
              className={cn(
                "size-4 shrink-0 transition-colors",
                isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground",
              )}
            />
            {!collapsed ? (
              <motion.span
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: "auto" }}
                exit={{ opacity: 0, width: 0 }}
                transition={transitionFast}
                className="truncate"
              >
                {item.name}
              </motion.span>
            ) : null}
          </Link>
        );
      })}
    </nav>
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
  const { toggleCollapsed } = useSidebar();

  return (
    <>
      <div
        className={cn(
          "flex h-14 shrink-0 items-center border-b border-sidebar-border sm:h-16",
          collapsed ? "justify-center px-2" : "justify-between px-3",
        )}
      >
        {!collapsed ? (
          <Link href={routes.dashboard} className="flex items-center gap-2.5 px-1">
            <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-xs font-bold text-primary-foreground">
              AI
            </span>
            <span className="text-sm font-semibold tracking-tight">Knowledge</span>
          </Link>
        ) : (
          <Link
            href={routes.dashboard}
            className="flex size-8 items-center justify-center rounded-lg bg-primary text-xs font-bold text-primary-foreground"
            aria-label="Dashboard"
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
      <ScrollArea className="flex-1 py-3">
        <SidebarNav collapsed={collapsed} onNavigate={onNavigate} />
      </ScrollArea>
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
