import {
  motion,
  useScroll,
  useTransform,
} from 'framer-motion'
import { Link } from 'react-router-dom'

function Header({
  dark = false,
}) {
  const {
    scrollY,
  } = useScroll()

  const backgroundColor =
    useTransform(
      scrollY,
      [
        0,
        80,
        320,
      ],
      [
        'rgba(184,212,244,0)',
        'rgba(201,221,245,0.52)',
        'rgba(240,245,250,0.97)',
      ],
    )

  const borderColor =
    useTransform(
      scrollY,
      [
        0,
        100,
        320,
      ],
      [
        'rgba(74,102,164,0)',
        'rgba(74,102,164,0.08)',
        'rgba(74,102,164,0.16)',
      ],
    )

  if (dark) {
    return (
      <header className="sticky top-0 z-50 border-b border-white/[0.08] bg-[#050505] text-white">
        <NavContent dark />
      </header>
    )
  }

  return (
    <motion.header
      style={{
        backgroundColor,
        borderColor,
      }}
      className="fixed inset-x-0 top-0 z-50 border-b"
    >
      <NavContent />
    </motion.header>
  )
}

function NavContent({
  dark = false,
}) {
  const textClass =
    dark
      ? 'text-[#aeb6c5] hover:text-white'
      : 'text-[#36517d] hover:text-[#092765]'

  return (
    <div className="mx-auto flex h-[68px] max-w-[1440px] items-center px-6 sm:px-8 lg:px-12">
      <Link
        to="/"
        className="flex shrink-0 items-center gap-3"
      >
        <div className="flex h-8 w-8 items-center justify-center bg-[#1d4ed8]">
          <div className="h-3 w-3 border border-white" />
        </div>

        <span
          className={
            dark
              ? 'text-[17px] font-semibold tracking-[-0.025em] text-white'
              : 'text-[17px] font-semibold tracking-[-0.025em] text-[#071938]'
          }
        >
          SkillSync
        </span>
      </Link>

      <nav className="ml-12 hidden items-center gap-7 lg:flex">
        <a
          href="/#why"
          className={`text-[13px] font-medium transition-colors ${textClass}`}
        >
          Product
        </a>

        <a
          href="/#evidence"
          className={`text-[13px] font-medium transition-colors ${textClass}`}
        >
          Evidence
        </a>

        <a
          href="/#engine"
          className={`text-[13px] font-medium transition-colors ${textClass}`}
        >
          How it works
        </a>

        <a
          href="/#report-preview"
          className={`text-[13px] font-medium transition-colors ${textClass}`}
        >
          Report
        </a>

        <a
          href="/#analyzer"
          className={`text-[13px] font-medium transition-colors ${textClass}`}
        >
          Analyzer
        </a>
      </nav>

      <div className="ml-auto flex items-center gap-2">
        <a
          href="/#why"
          className={
            dark
              ? 'hidden px-4 py-2.5 text-[13px] font-medium text-[#bac3d3] transition-colors hover:text-white sm:inline-flex'
              : 'hidden px-4 py-2.5 text-[13px] font-medium text-[#36517d] transition-colors hover:text-[#092765] sm:inline-flex'
          }
        >
          Explore platform
        </a>

        <a
          href="/#analyzer"
          className="hidden border border-[#5678c5]/35 bg-[#dbe6ff]/55 px-4 py-2.5 text-[13px] font-semibold text-[#19479d] transition-colors hover:bg-[#cfddfb] md:inline-flex"
        >
          Try analyzer
        </a>

        <a
          href="/#analyzer"
          className="inline-flex bg-[#1d4ed8] px-5 py-2.5 text-[13px] font-semibold text-white transition-colors hover:bg-[#153ea9]"
        >
          Get started
        </a>
      </div>
    </div>
  )
}

export default Header
