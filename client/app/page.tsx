import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-6 bg-zinc-50 px-4 text-center dark:bg-zinc-950">
      <div className="flex flex-col items-center gap-2">
        <Image src="/favicon-no-bg.png" alt="Unlocked" width={40} height={40} />
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">Unlocked</h1>
        <p className="mt-1 text-sm text-zinc-500">Admin console and user verification</p>
      </div>
      <div className="flex gap-3">
        <Link href="/login" className="btn-primary">
          Sign in
        </Link>
        <Link href="/signup" className="btn-secondary">
          Verify identity
        </Link>
      </div>
      <Link href="/admin/login" className="text-xs font-semibold text-zinc-400">
        Admin sign in
      </Link>
    </div>
  );
}
