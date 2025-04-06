"use client"

import * as React from "react"
import type { TooltipProps } from "recharts"
import * as RechartsPrimitive from "recharts"

import { cn } from "@/lib/utils"

// Format: { THEME_NAME: CSS_SELECTOR }
const THEMES = { light: "", dark: ".dark" } as const

interface ChartConfig {
  [key: string]: {
    label: string
    color: string
  }
}

type ChartContextValue = {
  config: ChartConfig
}

const ChartContext = React.createContext<ChartContextValue | null>(null)

function useChartContext() {
  const context = React.useContext(ChartContext)
  if (!context) {
    throw new Error("useChartContext must be used within a ChartContainer")
  }
  return context
}

interface ChartContainerProps {
  config: ChartConfig
  className?: string
  children: React.ReactNode
}

function ChartContainer({ config, className, children }: ChartContainerProps) {
  // Create CSS variables for each color in the config
  const style = React.useMemo(() => {
    return Object.entries(config).reduce(
      (acc, [key, value]) => {
        acc[`--color-${key}`] = value.color
        return acc
      },
      {} as Record<string, string>,
    )
  }, [config])

  return (
    <ChartContext.Provider value={{ config }}>
      <div className={cn("", className)} style={style}>
        {children}
      </div>
    </ChartContext.Provider>
  )
}

const ChartStyle = ({ id, config }: { id: string; config: ChartConfig }) => {
  const colorConfig = Object.entries(config).filter(([_, config]) => config.color)

  if (!colorConfig.length) {
    return null
  }

  return (
    <style
      dangerouslySetInnerHTML={{
        __html: Object.entries(THEMES)
          .map(
            ([theme, prefix]) => `
${prefix} [data-chart=${id}] {
${colorConfig
  .map(([key, itemConfig]) => {
    const color = itemConfig.color
    return color ? `  --color-${key}: ${color};` : null
  })
  .join("\n")}
}
`,
          )
          .join("\n"),
      }}
    />
  )
}

// Re-export the recharts TooltipProps type
type ChartTooltipProps = TooltipProps<any, any>

interface ChartTooltipContentProps {
  active?: boolean
  payload?: any[]
  label?: string
  className?: string
}

function ChartTooltipContent({ active, payload, label, className }: ChartTooltipContentProps) {
  const { config } = useChartContext()

  if (!active || !payload?.length) {
    return null
  }

  return (
    <div className={cn("rounded-lg border bg-background p-2 shadow-sm", className)}>
      <div className="text-xs font-medium">{label}</div>
      <div className="mt-1 flex flex-col gap-0.5">
        {payload.map((item, index) => {
          const dataKey = item.dataKey as string
          const configItem = config[dataKey]

          if (!configItem) {
            return null
          }

          return (
            <div key={index} className="flex items-center gap-1 text-xs">
              <div className="h-2 w-2 rounded-full" style={{ backgroundColor: configItem.color }} />
              <span className="font-medium">{configItem.label}:</span>
              <span>{item.value}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// Re-export the recharts Tooltip component as ChartTooltip
function ChartTooltip(props: ChartTooltipProps) {
  // This is just a pass-through to the recharts Tooltip component
  // We're re-exporting it to keep the naming consistent
  const { content, ...rest } = props

  // @ts-ignore - recharts types are not fully compatible
  return <RechartsPrimitive.Tooltip content={content} {...rest} />
}

const ChartLegend = RechartsPrimitive.Legend

const ChartLegendContent = React.forwardRef<
  HTMLDivElement,
  React.ComponentProps<"div"> &
    Pick<RechartsPrimitive.LegendProps, "payload" | "verticalAlign"> & {
      hideIcon?: boolean
      nameKey?: string
    }
>(({ className, hideIcon = false, payload, verticalAlign = "bottom", nameKey }, ref) => {
  const { config } = useChartContext()

  if (!payload?.length) {
    return null
  }

  return (
    <div
      ref={ref}
      className={cn("flex items-center justify-center gap-4", verticalAlign === "top" ? "pb-3" : "pt-3", className)}
    >
      {payload.map((item) => {
        const key = `${nameKey || item.dataKey || "value"}`
        const itemConfig = config[key as keyof typeof config]

        return (
          <div
            key={item.value}
            className={cn("flex items-center gap-1.5 [&>svg]:h-3 [&>svg]:w-3 [&>svg]:text-muted-foreground")}
          >
            {itemConfig?.icon && !hideIcon ? (
              <itemConfig.icon />
            ) : (
              <div
                className="h-2 w-2 shrink-0 rounded-[2px]"
                style={{
                  backgroundColor: item.color,
                }}
              />
            )}
            {itemConfig?.label}
          </div>
        )
      })}
    </div>
  )
})
ChartLegendContent.displayName = "ChartLegend"

// Helper to extract item config from a payload.
function getPayloadConfigFromPayload(config: ChartConfig, payload: unknown, key: string) {
  if (typeof payload !== "object" || payload === null) {
    return undefined
  }

  const payloadPayload =
    "payload" in payload && typeof payload.payload === "object" && payload.payload !== null
      ? payload.payload
      : undefined

  let configLabelKey: string = key

  if (key in payload && typeof payload[key as keyof typeof payload] === "string") {
    configLabelKey = payload[key as keyof typeof payload] as string
  } else if (
    payloadPayload &&
    key in payloadPayload &&
    typeof payloadPayload[key as keyof typeof payloadPayload] === "string"
  ) {
    configLabelKey = payloadPayload[key as keyof typeof payloadPayload] as string
  }

  return configLabelKey in config ? config[configLabelKey] : config[key as keyof typeof config]
}

export {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
  ChartStyle,
  useChartContext,
}

