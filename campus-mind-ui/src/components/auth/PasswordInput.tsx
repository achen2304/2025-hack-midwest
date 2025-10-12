"use client"

import { useState, forwardRef } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Eye, EyeOff } from "lucide-react";
import { cn } from "@/lib/utils";

interface PasswordInputProps extends React.ComponentProps<typeof Input> {
  showStrength?: boolean;
  onStrengthChange?: (strength: number) => void;
}

export const PasswordInput = forwardRef<HTMLInputElement, PasswordInputProps>(
  ({ className, showStrength = false, onStrengthChange, ...props }, ref) => {
    const [showPassword, setShowPassword] = useState(false);
    const [strength, setStrength] = useState(0);

    const calculateStrength = (password: string): number => {
      let score = 0;
      if (password.length >= 8) score++;
      if (/[A-Z]/.test(password)) score++;
      if (/[0-9]/.test(password)) score++;
      if (/[^A-Za-z0-9]/.test(password)) score++;
      return score;
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (showStrength) {
        const newStrength = calculateStrength(e.target.value);
        setStrength(newStrength);
        onStrengthChange?.(newStrength);
      }
      props.onChange?.(e);
    };

    const getStrengthLabel = () => {
      switch (strength) {
        case 0:
        case 1:
          return "Weak";
        case 2:
          return "Okay";
        case 3:
          return "Strong";
        case 4:
          return "Very Strong";
        default:
          return "";
      }
    };

    const getStrengthColor = () => {
      switch (strength) {
        case 0:
        case 1:
          return "bg-destructive";
        case 2:
          return "bg-warning";
        case 3:
          return "bg-success";
        case 4:
          return "bg-success";
        default:
          return "bg-muted";
      }
    };

    return (
      <div className="space-y-2">
        <div className="relative">
          <Input
            {...props}
            ref={ref}
            type={showPassword ? "text" : "password"}
            className={cn("pr-10", className)}
            onChange={handleChange}
          />
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
            onClick={() => setShowPassword(!showPassword)}
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? (
              <EyeOff className="h-4 w-4 text-muted-foreground" />
            ) : (
              <Eye className="h-4 w-4 text-muted-foreground" />
            )}
          </Button>
        </div>
        {showStrength && props.value && (
          <div className="space-y-1">
            <div className="flex gap-1">
              {[...Array(4)].map((_, i) => (
                <div
                  key={i}
                  className={cn(
                    "h-1 flex-1 rounded-full transition-colors",
                    i < strength ? getStrengthColor() : "bg-muted"
                  )}
                />
              ))}
            </div>
            {strength > 0 && (
              <p className="text-xs text-muted-foreground">
                Strength: {getStrengthLabel()}
              </p>
            )}
          </div>
        )}
      </div>
    );
  }
);

PasswordInput.displayName = "PasswordInput";
