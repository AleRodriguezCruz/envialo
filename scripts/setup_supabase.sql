-- Crear bucket "transfers"
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'transfers',
    'transfers',
    false,
    104857600,
    ARRAY['image/jpeg','image/png','image/gif','image/webp',
          'application/pdf','application/zip','text/plain',
          'video/mp4','audio/mpeg']
)
ON CONFLICT (id) DO NOTHING;

-- Crear tabla audit_logs
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id              UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    transfer_token  TEXT        NOT NULL,
    action          TEXT        NOT NULL
                    CHECK (action IN ('upload','download','delete','expired','error')),
    metadata        JSONB       DEFAULT '{}'::jsonb,
    ip_address      TEXT,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_transfer_token
    ON public.audit_logs (transfer_token);

CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at
    ON public.audit_logs (created_at DESC);

-- Seguridad RLS
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Solo service_role puede insertar logs"
    ON public.audit_logs FOR INSERT TO service_role WITH CHECK (true);

CREATE POLICY "Solo service_role puede leer logs"
    ON public.audit_logs FOR SELECT TO service_role USING (true);

-- Políticas de Storage
CREATE POLICY "service_role puede subir archivos"
    ON storage.objects FOR INSERT TO service_role
    WITH CHECK (bucket_id = 'transfers');

CREATE POLICY "service_role puede leer archivos"
    ON storage.objects FOR SELECT TO service_role
    USING (bucket_id = 'transfers');

CREATE POLICY "service_role puede eliminar archivos"
    ON storage.objects FOR DELETE TO service_role
    USING (bucket_id = 'transfers');
```

