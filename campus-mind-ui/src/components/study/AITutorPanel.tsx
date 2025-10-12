"use client"

import { useState } from "react";
import { MessageCircle, Send, Sparkles } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const AITutorPanel = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hi! I'm CampusMind, your AI study assistant. Ask me anything about Linear Algebra or your study plan!",
    },
  ]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    
    setMessages([...messages, { role: "user", content: input }]);
    setInput("");
    
    // Simulate AI response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I can help you with that! Let me explain...",
        },
      ]);
    }, 1000);
  };

  return (
    <Card className="border-border bg-card p-4 shadow-card h-[500px] flex flex-col">
      <div className="flex items-center gap-2 pb-3 border-b border-border">
        <MessageCircle className="h-5 w-5 text-primary" />
        <div className="flex-1">
          <h3 className="font-semibold text-foreground">Ask CampusMind</h3>
          <p className="text-xs text-muted-foreground">
            Referencing: MATH 241 → Matrix Operations → Midterm 2
          </p>
        </div>
        <Sparkles className="h-4 w-4 text-accent" />
      </div>

      <ScrollArea className="flex-1 py-4">
        <div className="space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`rounded-lg px-4 py-2 max-w-[80%] ${
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-accent/10 text-foreground border border-border"
                }`}
              >
                <p className="text-sm">{message.content}</p>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>

      <div className="flex gap-2 pt-3 border-t border-border">
        <Input
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSend()}
          className="rounded-lg"
        />
        <Button onClick={handleSend} size="icon" className="flex-shrink-0">
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </Card>
  );
};

export default AITutorPanel;
