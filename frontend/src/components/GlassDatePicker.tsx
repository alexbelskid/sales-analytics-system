
"use client"

import * as React from "react"
import { format } from "date-fns"
import { Calendar as CalendarIcon, ChevronDown } from "lucide-react"

import { cn } from "@/lib/utils"
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"
import { Calendar } from "@/components/ui/calendar"
import LiquidButton from "@/components/LiquidButton"

export interface GlassDatePickerProps {
    value?: string | Date
    onChange?: (date: string) => void
    className?: string
}

const GlassDatePicker = React.forwardRef<HTMLButtonElement, GlassDatePickerProps>(
    ({ className, value, onChange }, ref) => {
        const date = value ? new Date(value) : undefined

        const handleSelect = (newDate: Date | undefined) => {
            if (newDate && onChange) {
                // Ensure we handle timezone offset correctly or just start of day string 
                // For simplicity and to match input type="date", we usually want YYYY-MM-DD
                // But date-fns format is safer.
                onChange(format(newDate, "yyyy-MM-dd"))
            }
        }

        return (
            <Popover>
                <PopoverTrigger asChild>
                    <LiquidButton
                        variant="secondary"
                        className={cn("min-w-[160px] justify-between px-4", className)}
                        ref={ref}
                    >
                        <span className="flex items-center gap-2">
                            <CalendarIcon className="h-4 w-4 opacity-50" />
                            {date ? format(date, "dd.MM.yyyy") : <span>Выберите дату</span>}
                        </span>
                    </LiquidButton>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0 bg-[#1A1A1A] border-[#333333] rounded-2xl shadow-xl backdrop-blur-xl">
                    <Calendar
                        mode="single"
                        selected={date}
                        onSelect={handleSelect}
                        initialFocus
                        className="rounded-md border-none text-gray-300"
                        classNames={{
                            day_selected: "bg-white text-black hover:bg-white/90 hover:text-black focus:bg-white focus:text-black",
                            day_today: "bg-white/10 text-white",
                            day: "h-9 w-9 p-0 font-normal aria-selected:opacity-100 hover:bg-white/5 hover:text-white rounded-md transition-all",
                            head_cell: "text-gray-500 rounded-md w-9 font-normal text-[0.8rem]",
                            cell: "h-9 w-9 text-center text-sm p-0 relative [&:has([aria-selected])]:bg-transparent focus-within:relative focus-within:z-20",
                            nav_button: "border-[#333333] hover:bg-white/5 hover:text-white",
                            caption: "text-white relative items-center justify-center pt-1",
                        }}
                    />
                </PopoverContent>
            </Popover>
        )
    }
)
GlassDatePicker.displayName = "GlassDatePicker"

export default GlassDatePicker
