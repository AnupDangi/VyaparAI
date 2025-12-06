import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { UploadCloud, X, Image as ImageIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface ImageUploadProps {
    value?: File | null;
    onChange: (file: File | null) => void;
    className?: string;
    previewUrl?: string; // Initial preview URL (e.g. for edit mode)
}

export function ImageUpload({ value, onChange, className, previewUrl }: ImageUploadProps) {
    const [currentPreview, setCurrentPreview] = useState<string | null>(previewUrl || null);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (value) {
            const objectUrl = URL.createObjectURL(value);
            setCurrentPreview(objectUrl);
            return () => URL.revokeObjectURL(objectUrl);
        } else if (previewUrl && !value) {
            setCurrentPreview(previewUrl);
        } else {
            setCurrentPreview(null);
        }
    }, [value, previewUrl]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            onChange(file);
        }
    };

    const clearImage = () => {
        onChange(null);
        if (inputRef.current) {
            inputRef.current.value = "";
        }
    };

    return (
        <div className={cn("w-full", className)}>
            <div
                className={cn(
                    "border-2 border-dashed rounded-lg p-4 flex flex-col items-center justify-center gap-4 transition-colors",
                    currentPreview ? "border-primary/50 bg-secondary/20" : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50",
                    "h-64 cursor-pointer relative"
                )}
                onClick={() => !currentPreview && inputRef.current?.click()}
            >
                <input
                    type="file"
                    ref={inputRef}
                    className="hidden"
                    accept="image/*"
                    onChange={handleFileChange}
                />

                {currentPreview ? (
                    <div className="relative w-full h-full flex items-center justify-center overflow-hidden rounded-md group">
                        <img
                            src={currentPreview}
                            alt="Preview"
                            className="object-contain max-w-full max-h-full"
                        />
                        <div className="absolute top-2 right-2 flex gap-2">
                            <Button
                                type="button"
                                variant="destructive"
                                size="icon"
                                className="h-8 w-8 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    clearImage();
                                }}
                            >
                                <X className="h-4 w-4" />
                            </Button>
                        </div>
                        {/* Overlay to change image */}
                        <div className="absolute inset-x-0 bottom-0 bg-black/60 text-white p-2 text-xs text-center translate-y-full group-hover:translate-y-0 transition-transform">
                            Click to change
                        </div>
                        <div
                            className="absolute inset-0 z-0"
                            onClick={() => inputRef.current?.click()}
                        />
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center text-center text-muted-foreground">
                        <div className="bg-primary/10 p-3 rounded-full mb-3">
                            <UploadCloud className="h-6 w-6 text-primary" />
                        </div>
                        <p className="font-medium text-sm">Click to upload image</p>
                        <p className="text-xs text-muted-foreground mt-1">SVG, PNG, JPG or GIF (max. 5MB)</p>
                    </div>
                )}
            </div>
        </div>
    );
}
