"use client"

import type React from "react"

import { useState } from "react"

const TOAST_LIMIT = 5
const TOAST_REMOVE_DELAY = 5000

type ToastActionElement = React.ReactElement<typeof import("./toast").ToastAction>

export type Toast = {
  id: string
  title?: React.ReactNode
  description?: React.ReactNode
  action?: ToastActionElement
  variant?: "default" | "destructive"
}

const actionTypes = {
  ADD_TOAST: "ADD_TOAST",
  UPDATE_TOAST: "UPDATE_TOAST",
  DISMISS_TOAST: "DISMISS_TOAST",
  REMOVE_TOAST: "REMOVE_TOAST",
} as const

let count = 0

function generateId() {
  return `${count++}`
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([])

  function toast({ title, description, action, variant }: Omit<Toast, "id">) {
    const id = generateId()

    const newToast = {
      id,
      title,
      description,
      action,
      variant,
    }

    setToasts((prevToasts) => [newToast, ...prevToasts].slice(0, TOAST_LIMIT))

    setTimeout(() => {
      setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id))
    }, TOAST_REMOVE_DELAY)

    return {
      id,
      dismiss: () => setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id)),
      update: (props: Omit<Toast, "id">) => {
        setToasts((prevToasts) => prevToasts.map((toast) => (toast.id === id ? { ...toast, ...props } : toast)))
      },
    }
  }

  return {
    toast,
    toasts,
    dismiss: (toastId?: string) => {
      setToasts((prevToasts) => (toastId ? prevToasts.filter((toast) => toast.id !== toastId) : []))
    },
  }
}

