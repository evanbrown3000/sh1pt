import { cookies } from 'next/headers';
import { createServerSupabase } from '@profullstack/stack/supabase';

// Anon-key server client that reads/writes the session cookie. Safe to
// use from Server Components (reads work fine), Server Actions and
// Route Handlers (reads + writes). The factory swallows the set error on
// Server Components since Next 15 forbids mutation during render —
// Supabase's token refresh will retry on the next request where it's
// legal.
export function getSupabaseServerClient() {
  return createServerSupabase(cookies());
}
