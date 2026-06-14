"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import {
  BookOpen,
  LayoutDashboard,
  LogIn,
  PanelLeftClose,
  PanelLeftOpen,
  UserPlus,
  X,
} from "lucide-react";

import { useSidebar } from "@/components/layout/sidebar-context";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { backdropVariants, sidebarTransition, transitionFast } from "@/lib/motion";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Home", href: "/", icon: BookOpen },
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Login", href: "/login", icon: LogIn },
  { name: "Register", href: "/register", icon: UserPlus },
];

const SIDEBAR_WIDTH_EXPANDED = 256;
const SIDEBAR_WIDTH_COLLAPSED = 64;

function SidebarNav({
  collapsed,
  onNavigate,
}: {
  collapsed: boolean;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-1 px-2">
      {navigation.map((item) => {
        const isActive = pathname === item.href;
        const Icon = item.icon;

        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            title={collapsed ? item.name : undefined}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors duration-200",
              collapsed && "justify-center px-2",
              isActive
                ? "bg-primary text-primary-foreground"
                : "text-text-secondary hover:bg-sidebar-accent hover:text-sidebar-foreground",
            )}
          >
            <Icon className="size-4 shrink-0" />
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
          "flex h-16 shrink-0 items-center border-b border-sidebar-border",
          collapsed ? "justify-center px-2" : "justify-between px-4",
        )}
      >
        {!collapsed ? (
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-base font-semibold tracking-tight"
          >
            AI Knowledge
          </motion.span>
        ) : (
          <span className="text-base font-bold text-primary">AI</span>
        )}
        {showCollapseToggle ? (
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={toggleCollapsed}
            className={cn(collapsed && "hidden md:inline-flex")}
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
      <ScrollArea className="flex-1 py-4">
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
              className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
              onClick={() => setMobileOpen(false)}
            />
            <motion.aside
              key="sidebar-drawer"
              initial={{ x: -SIDEBAR_WIDTH_EXPANDED }}
              animate={{ x: 0 }}
              exit={{ x: -SIDEBAR_WIDTH_EXPANDED }}
              transition={sidebarTransition}
              className="fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-sidebar-border bg-sidebar"
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
