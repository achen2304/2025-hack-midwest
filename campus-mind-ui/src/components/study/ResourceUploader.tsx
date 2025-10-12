import { FolderOpen, Upload, FileText } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";

interface ResourceUploaderProps {
  notes: string;
  onNotesChange: (value: string) => void;
}

const ResourceUploader = ({ notes, onNotesChange }: ResourceUploaderProps) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <FolderOpen className="h-5 w-5 text-primary" />
        <Label className="text-base font-semibold">Step 3: Add or Review Study Materials</Label>
      </div>

      <Card className="border-dashed border-2 border-border bg-accent/5 p-4">
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-foreground">Uploaded by Canvas</p>
              <p className="text-xs text-muted-foreground mt-1">
                lecture_07_matrices.pdf • Chapter_4_notes.docx • reading_links.txt
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 pt-3 border-t border-border">
            <Upload className="h-5 w-5 text-muted-foreground" />
            <div className="flex-1">
              <p className="text-sm font-medium text-foreground">Add Your Own Files</p>
              <button className="text-xs text-primary hover:underline mt-1">
                Click to upload or drag and drop
              </button>
            </div>
          </div>
        </div>
      </Card>

      <div className="space-y-2">
        <Label className="text-sm">Quick Notes Input</Label>
        <Textarea
          placeholder="Paste custom notes or key points here..."
          value={notes}
          onChange={(e) => onNotesChange(e.target.value)}
          className="rounded-lg min-h-[100px]"
        />
      </div>

      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <div className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
        AI analyzing course materials...
      </div>
    </div>
  );
};

export default ResourceUploader;
