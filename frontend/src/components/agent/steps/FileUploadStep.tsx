import { useCallback, useState } from 'react';
import { Upload, X, FileText, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useFiles } from '@/hooks/useFiles';

interface FileUploadStepProps {
  fileIds: string[];
  onChange: (fileIds: string[]) => void;
}

export function FileUploadStep({ fileIds, onChange }: FileUploadStepProps) {
  const { files, uploadFilesAsync, isUploading } = useFiles();
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const droppedFiles = Array.from(e.dataTransfer.files);
      if (droppedFiles.length === 0) return;

      try {
        const uploaded = await uploadFilesAsync(droppedFiles);
        const newIds = uploaded.map((f) => f.id);
        onChange([...fileIds, ...newIds]);
      } catch (err) {
        console.error('Upload failed:', err);
      }
    },
    [fileIds, onChange, uploadFilesAsync]
  );

  const handleFileInput = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFiles = Array.from(e.target.files || []);
      if (selectedFiles.length === 0) return;

      try {
        const uploaded = await uploadFilesAsync(selectedFiles);
        const newIds = uploaded.map((f) => f.id);
        onChange([...fileIds, ...newIds]);
      } catch (err) {
        console.error('Upload failed:', err);
      }
    },
    [fileIds, onChange, uploadFilesAsync]
  );

  const handleRemove = (fileId: string) => {
    onChange(fileIds.filter((id) => id !== fileId));
  };

  const selectedFiles = files.filter((f) => fileIds.includes(f.id));

  const formatSize = (bytes?: number) => {
    if (!bytes) return '-';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-1">파일 업로드</h3>
        <p className="text-sm text-muted-foreground">
          RAG에 사용할 문서를 업로드합니다. PDF, DOCX, TXT, MD, CSV 등을 지원합니다.
        </p>
      </div>

      {/* Drop Zone */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragOver
            ? 'border-primary bg-primary/5'
            : 'border-border hover:border-primary/50'
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
      >
        {isUploading ? (
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">업로드 중...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload className="h-8 w-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              파일을 드래그하여 업로드하거나
            </p>
            <label>
              <Button variant="outline" size="sm" asChild>
                <span>파일 선택</span>
              </Button>
              <input
                type="file"
                multiple
                className="hidden"
                accept=".pdf,.docx,.txt,.md,.csv,.xls,.xlsx"
                onChange={handleFileInput}
              />
            </label>
            <p className="text-xs text-muted-foreground mt-1">
              PDF, DOCX, TXT, MD, CSV, XLS/XLSX (최대 50MB)
            </p>
          </div>
        )}
      </div>

      {/* Selected Files List */}
      {selectedFiles.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium">
            선택된 파일 ({selectedFiles.length})
          </p>
          <div className="space-y-1">
            {selectedFiles.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-2 rounded-md bg-muted/50"
              >
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">{file.filename}</span>
                  <Badge variant="outline" className="text-xs">
                    {formatSize(file.file_size)}
                  </Badge>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={() => handleRemove(file.id)}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      <p className="text-xs text-muted-foreground">
        파일 없이도 Agent를 생성할 수 있습니다. 웹 검색이나 API 도구만 사용할 수도 있습니다.
      </p>
    </div>
  );
}
