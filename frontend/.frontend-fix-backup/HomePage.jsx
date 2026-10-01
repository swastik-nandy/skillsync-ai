import {
  AnimatePresence,
  motion,
  useScroll,
  useTransform,
} from 'framer-motion'
import {
  ArrowRight,
  Check,
  LoaderCircle,
  FileText,
  Search,
  Sparkles,
  Upload,
} from 'lucide-react'
import {
  useEffect,
  useRef,
  useState,
} from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/Header'

const API_URL =
  import.meta.env.VITE_API_URL ||
  'http://localhost:8000'

const rotatingWords = [
  'evidence',
  'context',
  'requirements',
  'gaps',
]

const ticker = [
  'RESUME PARSING',
  'SEMANTIC RETRIEVAL',
  'BM25 SEARCH',
  'EVIDENCE MATCHING',
  'STRUCTURED ANALYSIS',
  'ROLE ALIGNMENT',
]

function Container({
  children,
  className = '',
}) {
  return (
    <div
      className={`mx-auto w-[calc(100%-32px)] max-w-[1240px] sm:w-[calc(100%-48px)] ${className}`}
    >
      {children}
    </div>
  )
}

function Reveal({
  children,
  className = '',
  delay = 0,
}) {
  return (
    <motion.div
      className={className}
      initial={{
        opacity: 0,
        y: 38,
      }}
      whileInView={{
        opacity: 1,
        y: 0,
      }}
      viewport={{
        once: true,
        amount: 0.16,
      }}
      transition={{
        duration: 0.7,
        delay,
        ease: [0.16, 1, 0.3, 1],
      }}
    >
      {children}
    </motion.div>
  )
}

function RotatingText() {
  const [index, setIndex] =
    useState(0)

  useEffect(() => {
    const timer =
      setInterval(() => {
        setIndex(
          (current) =>
            (current + 1) %
            rotatingWords.length,
        )
      }, 1900)

    return () =>
      clearInterval(timer)
  }, [])

  return (
    <span className="inline-flex min-w-[190px] overflow-hidden text-[#1d4ed8] sm:min-w-[270px]">
      <AnimatePresence mode="wait">
        <motion.span
          key={rotatingWords[index]}
          initial={{
            y: 46,
            opacity: 0,
          }}
          animate={{
            y: 0,
            opacity: 1,
          }}
          exit={{
            y: -46,
            opacity: 0,
          }}
          transition={{
            duration: 0.35,
          }}
        >
          {rotatingWords[index]}
        </motion.span>
      </AnimatePresence>
    </span>
  )
}

function Artwork({
  label,
  dark = false,
}) {
  return (
    <div
      className={`visual-grid flex aspect-[16/10] flex-col justify-between border p-6 ${
        dark
          ? 'border-[#31518e] bg-[#0d2457] text-[#8eacf0]'
          : 'border-[#a8bce8] bg-[#edf2ff] text-[#4f69a3]'
      }`}
    >
      <div className="flex justify-between text-[9px] font-semibold uppercase tracking-[0.17em]">
        <span>
          Image placeholder
        </span>

        <span>
          Coming later
        </span>
      </div>

      <div>
        <div
          className={`mb-5 h-px ${
            dark
              ? 'bg-[#31518e]'
              : 'bg-[#acbde5]'
          }`}
        />

        <p className="max-w-[420px] text-[12px] leading-5">
          {label}
        </p>
      </div>
    </div>
  )
}

function Hero() {
  const sectionRef =
    useRef(null)

  const {
    scrollYProgress,
  } = useScroll({
    target: sectionRef,
    offset: [
      'start start',
      'end start',
    ],
  })

  const backgroundColor =
    useTransform(
      scrollYProgress,
      [
        0,
        0.38,
        0.72,
        1,
      ],
      [
        '#b8d4f4',
        '#c9ddf5',
        '#dce8f7',
        '#f0f5fa',
      ],
    )

  const headingColor =
    useTransform(
      scrollYProgress,
      [
        0,
        0.55,
        1,
      ],
      [
        '#071938',
        '#0a214d',
        '#172447',
      ],
    )

  const bodyColor =
    useTransform(
      scrollYProgress,
      [
        0,
        0.55,
        1,
      ],
      [
        '#38547f',
        '#49638a',
        '#5b6883',
      ],
    )

  const glowOpacity =
    useTransform(
      scrollYProgress,
      [
        0,
        0.5,
        1,
      ],
      [
        0.55,
        0.32,
        0.08,
      ],
    )

  return (
    <motion.section
      ref={sectionRef}
      style={{
        backgroundColor,
      }}
      className="relative min-h-screen overflow-hidden pt-[68px]"
    >
      <div className="pointer-events-none absolute inset-0 overflow-hidden">

        <div
          className="absolute inset-0"
          style={{
            background: `
              radial-gradient(
                90% 95% at -5% -8%,
                rgba(44, 103, 196, 0.32) 0%,
                rgba(70, 132, 211, 0.18) 28%,
                rgba(113, 164, 218, 0.08) 50%,
                transparent 70%
              ),
              radial-gradient(
                74% 82% at 105% 8%,
                rgba(55, 119, 202, 0.24) 0%,
                rgba(93, 151, 210, 0.14) 34%,
                transparent 70%
              ),
              radial-gradient(
                78% 70% at 72% 105%,
                rgba(82, 137, 211, 0.20) 0%,
                rgba(146, 185, 226, 0.12) 42%,
                transparent 72%
              ),
              radial-gradient(
                52% 58% at 47% 45%,
                rgba(255, 255, 255, 0.16) 0%,
                rgba(213, 225, 255, 0.08) 42%,
                transparent 76%
              )
            `,
          }}
        />

        <div
          className="absolute inset-0"
          style={{
            background: `
              linear-gradient(
                116deg,
                rgba(255,255,255,0) 18%,
                rgba(230,237,255,0.08) 34%,
                rgba(255,255,255,0.28) 48%,
                rgba(140,184,228,0.10) 61%,
                rgba(255,255,255,0) 78%
              )
            `,
          }}
        />

        <div
          className="absolute inset-0 opacity-70"
          style={{
            background: `
              linear-gradient(
                155deg,
                rgba(45,87,190,0.05) 0%,
                transparent 32%,
                rgba(255,255,255,0.14) 49%,
                transparent 66%,
                rgba(82,111,196,0.05) 100%
              )
            `,
          }}
        />

        <div
          className="absolute -left-[14%] top-[18%] h-[42%] w-[72%] rotate-[-8deg]"
          style={{
            background: `
              linear-gradient(
                90deg,
                transparent,
                rgba(55,120,198,0.07),
                rgba(220,239,252,0.18),
                rgba(76,118,222,0.05),
                transparent
              )
            `,
            filter: 'blur(2px)',
          }}
        />

        <div
          className="absolute -right-[20%] top-[38%] h-[42%] w-[76%] rotate-[9deg]"
          style={{
            background: `
              linear-gradient(
                90deg,
                transparent,
                rgba(105,137,216,0.04),
                rgba(142,183,222,0.16),
                transparent
              )
            `,
          }}
        />

        <svg
          viewBox="0 0 1600 900"
          preserveAspectRatio="none"
          className="absolute inset-0 h-full w-full"
          aria-hidden="true"
        >
          <defs>
            <linearGradient
              id="heroSignalA"
              x1="0"
              y1="0"
              x2="1"
              y2="0"
            >
              <stop
                offset="0%"
                stopColor="#245fae"
                stopOpacity="0"
              />

              <stop
                offset="22%"
                stopColor="#245fae"
                stopOpacity="0.05"
              />

              <stop
                offset="52%"
                stopColor="#2868b7"
                stopOpacity="0.22"
              />

              <stop
                offset="82%"
                stopColor="#4d82ba"
                stopOpacity="0.11"
              />

              <stop
                offset="100%"
                stopColor="#4d82ba"
                stopOpacity="0"
              />
            </linearGradient>

            <linearGradient
              id="heroSignalB"
              x1="0"
              y1="0"
              x2="0"
              y2="1"
            >
              <stop
                offset="0%"
                stopColor="#326cac"
                stopOpacity="0"
              />

              <stop
                offset="30%"
                stopColor="#326cac"
                stopOpacity="0.13"
              />

              <stop
                offset="70%"
                stopColor="#668fb8"
                stopOpacity="0.16"
              />

              <stop
                offset="100%"
                stopColor="#668fb8"
                stopOpacity="0"
              />
            </linearGradient>

            <linearGradient
              id="heroSignalFine"
              x1="0"
              y1="0"
              x2="1"
              y2="1"
            >
              <stop
                offset="0%"
                stopColor="#2566b1"
                stopOpacity="0"
              />

              <stop
                offset="48%"
                stopColor="#2566b1"
                stopOpacity="0.10"
              />

              <stop
                offset="100%"
                stopColor="#5688bc"
                stopOpacity="0"
              />
            </linearGradient>
          </defs>

          <path
            d="M-100 285C180 220 390 205 600 250C805 294 920 390 1105 395C1295 400 1430 315 1700 260"
            fill="none"
            stroke="url(#heroSignalA)"
            strokeWidth="1.1"
          />

          <path
            d="M-120 340C160 275 390 270 590 315C790 360 925 445 1110 450C1300 455 1460 370 1710 320"
            fill="none"
            stroke="url(#heroSignalA)"
            strokeWidth="0.8"
          />

          <path
            d="M425 715C640 635 790 600 960 628C1120 653 1250 730 1420 680C1505 655 1590 610 1700 555"
            fill="none"
            stroke="url(#heroSignalA)"
            strokeWidth="1"
          />

          <path
            d="M1085 -100C1010 100 1020 250 1100 380C1185 515 1200 665 1125 980"
            fill="none"
            stroke="url(#heroSignalB)"
            strokeWidth="0.9"
          />

          <path
            d="M1240 -100C1175 105 1195 250 1280 370C1375 505 1390 660 1325 960"
            fill="none"
            stroke="url(#heroSignalB)"
            strokeWidth="0.8"
          />

          <path
            d="M1390 -100C1340 95 1360 240 1445 355C1535 480 1570 600 1540 840"
            fill="none"
            stroke="url(#heroSignalB)"
            strokeWidth="0.7"
          />

          <path
            d="M655 100L1370 735"
            fill="none"
            stroke="url(#heroSignalFine)"
            strokeWidth="0.7"
          />

          <path
            d="M735 65L1450 700"
            fill="none"
            stroke="url(#heroSignalFine)"
            strokeWidth="0.55"
          />

          <path
            d="M900 510C1015 475 1100 490 1180 545C1260 600 1365 595 1495 525"
            fill="none"
            stroke="url(#heroSignalA)"
            strokeWidth="0.75"
          />
        </svg>

        <div
          className="absolute inset-x-0 bottom-0 h-[38%]"
          style={{
            background: `
              linear-gradient(
                to top,
                rgba(216,233,248,0.42) 0%,
                rgba(203,226,246,0.18) 42%,
                transparent 100%
              )
            `,
          }}
        />

        <div
          className="absolute inset-x-0 top-0 h-[22%]"
          style={{
            background: `
              linear-gradient(
                to bottom,
                rgba(191,209,247,0.22),
                transparent
              )
            `,
          }}
        />
      </div>

      <Container className="relative grid min-h-[calc(100vh-68px)] items-center gap-16 py-20 lg:grid-cols-[0.9fr_1.1fr]">
        <motion.div
          initial={{
            opacity: 0,
            y: 30,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            duration: 0.75,
          }}
        >
          <motion.div
            style={{
              color: bodyColor,
            }}
            className="text-[10px] font-semibold uppercase tracking-[0.2em]"
          >
            SkillSync / Resume intelligence
          </motion.div>

          <motion.h1
            style={{
              color:
                headingColor,
            }}
            className="mt-5 text-[58px] font-semibold leading-[1.08] tracking-[-0.045em] sm:text-[76px] lg:text-[92px]"
          >
            Stop guessing.
            <br />
            See the
            <br />
            <RotatingText />
          </motion.h1>

          <motion.p
            style={{
              color:
                bodyColor,
            }}
            className="mt-8 max-w-[600px] text-[16px] leading-7"
          >
            SkillSync compares your actual resume with the exact role you are applying for and maps every important requirement to real evidence.
          </motion.p>

          <div className="mt-8 flex flex-wrap gap-3">
            <button
              type="button"
              className="inline-flex min-w-[148px] items-center justify-center gap-3 bg-[#1d4ed8] px-7 py-4 text-[14px] font-semibold text-white transition duration-200 hover:bg-[#173fac]"
            >
              Sign up now
              <ArrowRight size={16} />
            </button>

            <a
              href="#why"
              className="inline-flex min-w-[148px] items-center justify-center border border-[#6f8fd6] bg-[#dce7ff]/80 px-7 py-4 text-[14px] font-semibold text-[#1744ad] backdrop-blur-sm transition duration-200 hover:bg-[#d1dfff]"
            >
              Learn more
            </a>
          </div>
        </motion.div>

        <Reveal>
          <div className="relative min-h-[470px]">
            <div className="absolute inset-0 bg-[#dbe7ff]/10" />

            <svg
              viewBox="0 0 620 520"
              className="relative h-full min-h-[470px] w-full"
              aria-hidden="true"
            >
              <rect
                x="105"
                y="70"
                width="250"
                height="330"
                rx="2"
                fill="rgba(248,250,255,0.82)"
                stroke="#8eabed"
                strokeWidth="1.3"
              />

              <line
                x1="145"
                y1="120"
                x2="305"
                y2="120"
                stroke="#6387dd"
                strokeWidth="2"
                opacity="0.8"
              />

              <line
                x1="145"
                y1="155"
                x2="285"
                y2="155"
                stroke="#9eb7ed"
                strokeWidth="1.5"
              />

              <line
                x1="145"
                y1="185"
                x2="315"
                y2="185"
                stroke="#9eb7ed"
                strokeWidth="1.5"
              />

              <line
                x1="145"
                y1="215"
                x2="270"
                y2="215"
                stroke="#9eb7ed"
                strokeWidth="1.5"
              />

              <line
                x1="145"
                y1="275"
                x2="305"
                y2="275"
                stroke="#9eb7ed"
                strokeWidth="1.5"
              />

              <line
                x1="145"
                y1="305"
                x2="295"
                y2="305"
                stroke="#9eb7ed"
                strokeWidth="1.5"
              />

              <path
                d="M355 145C430 145 438 112 500 112"
                fill="none"
                stroke="#4c7be7"
                strokeWidth="1.5"
              />

              <path
                d="M355 225C430 225 445 250 515 250"
                fill="none"
                stroke="#6e90df"
                strokeWidth="1.5"
              />

              <path
                d="M355 320C425 320 455 380 515 380"
                fill="none"
                stroke="#91a9df"
                strokeWidth="1.5"
              />

              <circle
                cx="512"
                cy="112"
                r="6"
                fill="#3167df"
              />

              <circle
                cx="527"
                cy="250"
                r="6"
                fill="#6484cd"
              />

              <circle
                cx="527"
                cy="380"
                r="6"
                fill="#8ca6df"
              />

              <text
                x="530"
                y="117"
                fill="#224caa"
                fontSize="11"
                fontWeight="600"
              >
                SUPPORTED
              </text>

              <text
                x="545"
                y="255"
                fill="#47649c"
                fontSize="11"
                fontWeight="600"
              >
                PARTIAL
              </text>

              <text
                x="545"
                y="385"
                fill="#61759e"
                fontSize="11"
                fontWeight="600"
              >
                GAP
              </text>
            </svg>
          </div>
        </Reveal>
      </Container>
    </motion.section>
  )
}


function MovingRail() {
  const items = [
    ...ticker,
    ...ticker,
  ]

  return (
    <section className="overflow-hidden bg-[#1552d6] py-9 text-white">
      <div className="marquee-track flex items-center">
        {items.map(
          (item, index) => (
            <div
              key={`${item}-${index}`}
              className="flex items-center"
            >
              <span className="px-10 text-[20px] font-semibold tracking-[-0.04em] sm:px-16 sm:text-[26px]">
                {item}
              </span>

              <span className="text-[#82a9ff]">
                /
              </span>
            </div>
          ),
        )}
      </div>
    </section>
  )
}


function OfferSection() {
  return (
    <section
      id="success-story"
      className="relative overflow-hidden bg-[#04233D] text-white"
    >
      <div className="relative hidden xl:block">
        <div className="ml-auto w-[74%]">
          <img
            src={offerLetterImage}
            alt="A candidate receiving an offer letter"
            className="block h-auto w-full"
          />
        </div>

        <div
          className="pointer-events-none absolute inset-y-0 left-0 w-[60%]"
          style={{
            background: `
              linear-gradient(
                to right,
                #04233D 0%,
                #04233D 48%,
                rgba(4,35,61,0.98) 61%,
                rgba(4,35,61,0.82) 72%,
                rgba(4,35,61,0.42) 86%,
                transparent 100%
              )
            `,
          }}
        />

        <div
          className="pointer-events-none absolute inset-y-0 left-0 w-[48%]"
          style={{
            background: `
              radial-gradient(
                ellipse 95% 82% at 18% 45%,
                rgba(40,97,141,0.32) 0%,
                rgba(40,97,141,0.11) 48%,
                transparent 76%
              )
            `,
          }}
        />

        <Container className="absolute inset-0 z-10 flex items-center">
          <div className="w-[43%] max-w-[610px]">
            <Reveal>
              <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-[#D9B17E]">
                Outcome driven
              </div>

              <h2 className="mt-3 max-w-[12ch] text-[40px] leading-[1.02] tracking-[-0.04em] text-white 2xl:text-[46px]">
                Better evidence. Better applications.
              </h2>

              <p className="mt-4 max-w-[52ch] text-[13px] leading-6 text-[#D5E2EC] 2xl:text-[14px]">
                See what the role asks for, what your resume actually proves, and what still needs work before you apply.
              </p>

              <div className="mt-6 grid grid-cols-3 border-y border-white/[0.16]">
                <div className="border-r border-white/[0.16] py-4 pr-5">
                  <div className="text-[9px] font-semibold tracking-[0.16em] text-[#D9B17E]">
                    01
                  </div>

                  <div className="mt-2 text-[13px] font-semibold text-white">
                    Read the role
                  </div>

                  <p className="mt-1.5 text-[11px] leading-[1.55] text-[#B9CBD9]">
                    Turn the JD into clear requirements.
                  </p>
                </div>

                <div className="border-r border-white/[0.16] px-5 py-4">
                  <div className="text-[9px] font-semibold tracking-[0.16em] text-[#D9B17E]">
                    02
                  </div>

                  <div className="mt-2 text-[13px] font-semibold text-white">
                    Find evidence
                  </div>

                  <p className="mt-1.5 text-[11px] leading-[1.55] text-[#B9CBD9]">
                    See what your resume genuinely supports.
                  </p>
                </div>

                <div className="py-4 pl-5">
                  <div className="text-[9px] font-semibold tracking-[0.16em] text-[#D9B17E]">
                    03
                  </div>

                  <div className="mt-2 text-[13px] font-semibold text-white">
                    Apply sharper
                  </div>

                  <p className="mt-1.5 text-[11px] leading-[1.55] text-[#B9CBD9]">
                    Strengthen the gaps before sending.
                  </p>
                </div>
              </div>

              <div className="mt-5 grid grid-cols-3">
                <div className="border-l border-[#AB9680]/55 pl-3">
                  <div className="text-[11px] font-semibold text-[#E0C19A]">
                    Less guesswork
                  </div>

                  <div className="mt-1 text-[11px] text-[#B9CBD9]">
                    Know why you match.
                  </div>
                </div>

                <div className="border-l border-[#AB9680]/55 pl-3">
                  <div className="text-[11px] font-semibold text-[#E0C19A]">
                    Clearer gaps
                  </div>

                  <div className="mt-1 text-[11px] text-[#B9CBD9]">
                    Know what to improve.
                  </div>
                </div>

                <div className="border-l border-[#AB9680]/55 pl-3">
                  <div className="text-[11px] font-semibold text-[#E0C19A]">
                    More confidence
                  </div>

                  <div className="mt-1 text-[11px] text-[#B9CBD9]">
                    Apply with intent.
                  </div>
                </div>
              </div>

              <div className="mt-6 flex gap-3">
                <a
                  href="/#analyzer"
                  className="bg-white px-5 py-2.5 text-[12px] font-semibold text-[#04233D] transition-colors hover:bg-[#E8EFF5]"
                >
                  Analyze my resume
                </a>

                <a
                  href="/#report-preview"
                  className="border border-white/20 bg-white/[0.07] px-5 py-2.5 text-[12px] font-semibold text-white transition-colors hover:bg-white/[0.12]"
                >
                  Explore report
                </a>
              </div>
            </Reveal>
          </div>
        </Container>
      </div>

      <div className="xl:hidden">
        <div className="px-6 py-12 sm:px-8 sm:py-14">
          <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-[#D9B17E]">
            Outcome driven
          </div>

          <h2 className="mt-3 max-w-[12ch] text-[38px] font-semibold leading-[1.03] tracking-[-0.04em] text-white sm:text-[44px]">
            Better evidence. Better applications.
          </h2>

          <p className="mt-4 max-w-[48ch] text-[14px] leading-6 text-[#D5E2EC]">
            See what the role needs, what your resume proves, and what still needs work.
          </p>

          <div className="mt-6 flex flex-wrap gap-3">
            <a
              href="/#analyzer"
              className="bg-white px-5 py-3 text-[13px] font-semibold text-[#04233D]"
            >
              Analyze my resume
            </a>

            <a
              href="/#report-preview"
              className="border border-white/20 px-5 py-3 text-[13px] font-semibold text-white"
            >
              Explore report
            </a>
          </div>
        </div>

        <img
          src={offerLetterImage}
          alt="A candidate receiving an offer letter"
          className="block h-auto w-full"
        />
      </div>
    </section>
  )
}


function WhySection() {
  return (
    <section
      id="why"
      className="min-h-screen bg-[#e7eeff]"
    >
      <Container className="grid min-h-screen items-center gap-14 py-20 lg:grid-cols-2">
        <Reveal>
          <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#315ab7]">
            02 / The problem
          </div>

          <h2 className="mt-5 max-w-[650px] text-[43px] font-semibold leading-[1] tracking-[-0.035em] text-[#07142f] sm:text-[59px]">
            Most resume scores tell you almost nothing.
          </h2>

          <p className="mt-7 max-w-[570px] text-[14px] leading-7 text-[#53688f]">
            A single percentage hides the useful part. Which requirement matched? What evidence caused the match? Which skill is only implied? What is completely missing?
          </p>

          <p className="mt-5 max-w-[570px] text-[14px] leading-7 text-[#53688f]">
            SkillSync is being built around those questions instead of treating your resume like a bag of keywords.
          </p>
        </Reveal>

        <Reveal delay={0.08}>
          <Artwork label="Future illustration: traditional keyword score on one side, evidence-level SkillSync analysis on the other." />
        </Reveal>
      </Container>
    </section>
  )
}

function EvidenceSection() {
  const rows = [
    [
      '01',
      'Requirement',
      'Production Python experience',
    ],
    [
      '02',
      'Resume evidence',
      'FastAPI services serving 200+ queries per day',
    ],
    [
      '03',
      'Classification',
      'SUPPORTED',
    ],
  ]

  return (
    <section id="evidence" className="min-h-screen bg-[#02050a] text-white">
      <Container className="grid min-h-screen items-center gap-16 py-20 lg:grid-cols-[0.85fr_1.15fr]">
        <Reveal>
          <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#6f98ff]">
            03 / Evidence
          </div>

          <h2 className="mt-5 text-[43px] font-semibold leading-[1] tracking-[-0.035em] sm:text-[59px]">
            Evidence,
            <br />
            not keyword theatre.
          </h2>

          <p className="mt-7 max-w-[500px] text-[14px] leading-7 text-[#8191af]">
            SkillSync retrieves relevant resume context first, then evaluates the job requirement against that context.
          </p>
        </Reveal>

        <Reveal delay={0.08}>
          <div className="border border-[#1c2a43]">
            {rows.map(
              (
                [
                  number,
                  label,
                  value,
                ],
              ) => (
                <div
                  key={number}
                  className="grid grid-cols-[50px_120px_1fr] border-b border-[#1c2a43] px-5 py-6 last:border-b-0"
                >
                  <span className="text-[9px] text-[#52607a]">
                    {number}
                  </span>

                  <span className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[#6985bf]">
                    {label}
                  </span>

                  <span className="text-[12px] leading-5 text-[#d5ddeb]">
                    {value}
                  </span>
                </div>
              ),
            )}
          </div>
        </Reveal>
      </Container>
    </section>
  )
}

function Analyzer({
  onComplete,
}) {
  const [file, setFile] =
    useState(null)

  const [jd, setJd] =
    useState('')

  const [loading, setLoading] =
    useState(false)

  const [snapshot, setSnapshot] = useState(null)
  const requestRef = useRef(null)
  const progressRef = useRef(null)
  const [elapsedSeconds, setElapsedSeconds] = useState(0)

  const [error, setError] =
    useState('')

  const [parseResult, setParseResult] =
    useState(null)

  useEffect(() => () => requestRef.current?.abort(), [])

  useEffect(() => {
    if (loading) {
      progressRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })
      progressRef.current?.focus({ preventScroll: true })
    }
  }, [loading])

  useEffect(() => {
    if (!loading) return undefined
    const started = Date.now()
    const timer = setInterval(() => setElapsedSeconds(Math.floor((Date.now() - started) / 1000)), 1000)
    return () => clearInterval(timer)
  }, [loading])

  const submit = async () => {
    if (
      !file ||
      !jd.trim() ||
      loading
    ) {
      return
    }

    if (requestRef.current) return
    const controller = new AbortController()
    requestRef.current = controller
    setElapsedSeconds(0)
    setError('')
    setParseResult(null)
    setSnapshot(null)
    setLoading(true)

    try {
      const analysisForm =
        new FormData()

      analysisForm.append(
        'file',
        file,
      )

      analysisForm.append(
        'jd_text',
        jd.trim(),
      )

      const parseForm =
        new FormData()

      parseForm.append(
        'file',
        file,
      )

      const [
        analysisResponse,
        parseResponse,
      ] = await Promise.all([
        fetch(
          `${API_URL}/analysis/start`,
          {
            method: 'POST',
            body: analysisForm,
            signal: controller.signal,
          },
        ),

        fetch(
          `${API_URL}/resume/parse`,
          {
            method: 'POST',
            body: parseForm,
            signal: controller.signal,
          },
        ),
      ])

      const [
        analysisData,
        parseData,
      ] = await Promise.all([
        analysisResponse.json(),
        parseResponse.json(),
      ])

      if (!analysisResponse.ok) {
        throw new Error(
          analysisData?.detail ||
          'Unable to start analysis',
        )
      }

      if (!analysisData?.analysis_id) {
        throw new Error(
          'Analysis ID was not returned',
        )
      }

      sessionStorage.setItem(
        'skillsync_analysis_id',
        analysisData.analysis_id,
      )

      sessionStorage.removeItem(
        'skillsync_analysis_snapshot',
      )

      if (parseResponse.ok) {
        setParseResult(
          parseData
        )
      } else {
        setParseResult({
          parse_percentage: null,
          warning:
            parseData?.detail ||
            'Parsing diagnostics unavailable.',
        })
      }

      while (!controller.signal.aborted) {
        const response = await fetch(
          `${API_URL}/analysis/${encodeURIComponent(analysisData.analysis_id)}`,
          { signal: controller.signal },
        )
        const data = await response.json()
        if (!response.ok) throw new Error(data?.detail || 'Unable to load analysis progress')
        setSnapshot(data)
        if (data.status === 'failed') {
          throw new Error(data.sections?.feedback?.error || 'Analysis failed. Please retry.')
        }
        if (['completed', 'completed_with_errors'].includes(data.status)) {
          sessionStorage.setItem('skillsync_analysis_snapshot', JSON.stringify(data))
          // Keep the completed state visible before opening the populated report.
          await new Promise((resolve) => setTimeout(resolve, 350))
          if (!controller.signal.aborted) onComplete(analysisData.analysis_id)
          return
        }
        await new Promise((resolve) => setTimeout(resolve, 900))
      }

    } catch (
      requestError
    ) {
      if (controller.signal.aborted) return
      setError(
        requestError.message ||
        'Unable to analyze resume',
      )

      setLoading(false)
    } finally {
      if (requestRef.current === controller) requestRef.current = null
    }
  }

  return (
    <section
      id="analyzer"
      className="min-h-screen bg-white"
    >
      <Container className="grid min-h-screen items-center gap-14 py-20 lg:grid-cols-[0.72fr_1.28fr]">
        <Reveal>
          <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#315ab7]">
            04 / Analyzer
          </div>

          <h2 className="mt-5 text-[43px] font-semibold leading-[1] tracking-[-0.035em] text-[#07142f] sm:text-[59px]">
            One resume.
            <br />
            One target role.
          </h2>

          <p className="mt-7 max-w-[430px] text-[14px] leading-7 text-[#566b93]">
            Upload the exact resume you intend to send and paste the full job description.
          </p>
        </Reveal>

        <Reveal delay={0.08}>
          <div className="border border-[#aabce5] bg-[#f8faff] p-6 sm:p-8">
            <>
              <fieldset disabled={loading} hidden={loading}>
                <div className="mb-3 text-[10px] font-semibold uppercase tracking-[0.15em] text-[#526da5]">
                  Resume
                </div>

                <label className="flex min-h-[110px] cursor-pointer items-center gap-4 border border-dashed border-[#90a8db] bg-[#edf2ff] p-5">
                  <Upload
                    size={21}
                    className="text-[#315ab7]"
                  />

                  <div>
                    <div className="text-[13px] font-semibold text-[#152d5e]">
                      {file
                        ? file.name
                        : 'Choose resume'}
                    </div>

                    <div className="mt-1 text-[10px] text-[#6a7da4]">
                      PDF, DOCX or TXT
                    </div>
                  </div>

                  <input
                    type="file"
                    accept=".pdf,.docx,.txt"
                    className="hidden"
                    onChange={(
                      event,
                    ) =>
                      setFile(
                        event.target
                          .files?.[0] ||
                        null,
                      )
                    }
                  />
                </label>

                <div className="mb-3 mt-7 text-[10px] font-semibold uppercase tracking-[0.15em] text-[#526da5]">
                  Job description
                </div>

                <textarea
                  value={jd}
                  onChange={(
                    event,
                  ) =>
                    setJd(
                      event.target
                        .value,
                    )
                  }
                  rows={12}
                  placeholder="Paste the full job description..."
                  className="w-full resize-y border border-[#aabce5] bg-white p-4 text-[13px] leading-6 text-[#152d5e] outline-none focus:border-[#1d4ed8]"
                />

                {error && (
                  <div className="mt-4 border border-[#7e9edc] bg-[#e0e9ff] p-3 text-[11px] text-[#204999]">
                    {error}
                  </div>
                )}

              </fieldset>
                <button
                  type="button"
                  onClick={submit}
                  aria-busy={loading}
                  disabled={
                    loading || !file ||
                    !jd.trim()
                  }
                  className="mt-5 flex w-full items-center justify-center gap-3 bg-[#1d4ed8] px-5 py-4 text-[13px] font-semibold text-white disabled:bg-[#8fa6d9]"
                >
                  {loading ? <LoaderCircle size={20} className="parsing-spinner" aria-hidden="true" /> : <ArrowRight size={16} />}
                  {loading ? 'Analyzing your resume…' : 'Analyze resume'}
                </button>
              {loading && (
              <div ref={progressRef} tabIndex={-1} aria-busy="true" className="py-8 outline-none">
                <div aria-hidden="true" className="relative mx-auto mb-8 flex h-40 w-32 items-center justify-center overflow-hidden rounded-lg border border-[#aabce5] bg-white">
                  <FileText size={72} strokeWidth={1} className="text-[#90a8db]" />
                  <div className="resume-scan absolute inset-x-0 h-1 bg-[#1d4ed8] shadow-[0_0_24px_6px_#93b4ff]" />
                </div>
                <div className="mb-4 flex items-center gap-3 text-[#1d4ed8]" role="status">
                  <LoaderCircle size={24} className="parsing-spinner shrink-0" />
                  <span className="text-sm font-semibold">
                    {snapshot && ['completed', 'completed_with_errors'].includes(snapshot.status)
                      ? 'Analysis complete. Opening your report…'
                      : parseResult ? 'Analyzing your resume and calculating metrics…' : 'Uploading and parsing your resume…'}
                  </span>
                </div>
                <p className="mb-4 text-xs text-[#526da5]">{elapsedSeconds}s elapsed · Your report opens automatically when ready.</p>
                <div className="text-[10px] font-semibold uppercase tracking-[0.17em] text-[#315ab7]">
                  Building report
                </div>

                <h3 className="mt-4 text-[31px] font-semibold tracking-[-0.045em] text-[#07142f]">
                  Reading your evidence.
                </h3>

                {parseResult && (
                  <motion.div
                    initial={{
                      opacity: 0,
                      y: 8,
                    }}
                    animate={{
                      opacity: 1,
                      y: 0,
                    }}
                    className="mt-7 border border-[#b2c2e7] bg-white p-5"
                  >
                    <div className="flex items-end justify-between gap-6">
                      <div>
                        <div className="text-[9px] font-semibold uppercase tracking-[0.14em] text-[#7184ac]">
                          Parse coverage
                        </div>

                        <div className="mt-2 text-[11px] text-[#657aa5]">
                          {parseResult.parsed_units ?? 0}/
                          {parseResult.total_units ?? 0}{' '}
                          {parseResult.unit || 'unit'}
                          {(parseResult.total_units ?? 0) === 1
                            ? ''
                            : 's'} parsed
                        </div>

                        <div className="mt-1 text-[10px] text-[#8292b1]">
                          {parseResult.characters_extracted ?? 0}{' '}
                          characters extracted
                        </div>
                      </div>

                      <motion.div
                        initial={{
                          opacity: 0,
                          scale: 0.9,
                        }}
                        animate={{
                          opacity: 1,
                          scale: 1,
                        }}
                        className="text-[38px] font-semibold leading-none tracking-[-0.05em] text-[#1d4ed8]"
                      >
                        {parseResult.parse_percentage == null
                          ? 'N/A'
                          : `${parseResult.parse_percentage}%`}
                      </motion.div>
                    </div>

                    <div className="mt-4 h-[3px] overflow-hidden bg-[#d9e2f5]">
                      <motion.div
                        initial={{
                          width: 0,
                        }}
                        animate={{
                          width:
                            `${parseResult.parse_percentage ?? 0}%`,
                        }}
                        transition={{
                          duration: 0.55,
                          ease: [
                            0.16,
                            1,
                            0.3,
                            1,
                          ],
                        }}
                        className="h-full bg-[#1d4ed8]"
                      />
                    </div>

                    {parseResult.warning && (
                      <div className="mt-3 text-[10px] leading-5 text-[#7a5b18]">
                        {parseResult.warning}
                      </div>
                    )}
                  </motion.div>
                )}

                <div className="mt-9 border border-[#b2c2e7]">
                  {Object.entries(snapshot?.sections || {}).map(([key, section]) => (
                    <div key={key} className="flex items-center gap-3 border-b border-[#d5def1] px-4 py-4 last:border-b-0">
                      {section.status === 'completed'
                        ? <Check size={14} className="text-[#1d4ed8]" />
                        : section.status === 'running'
                          ? <LoaderCircle size={14} className="parsing-spinner text-[#1d4ed8]" />
                          : <span className="size-2 rounded-full bg-[#bdc9e5]" />}
                      <span className="flex-1 text-xs capitalize text-[#2f4b82]">{key.replaceAll('_', ' ')}</span>
                      <span className="text-[10px] uppercase text-[#7184ac]">{section.status}{section.elapsed_seconds != null ? ` · ${section.elapsed_seconds}s` : ''}</span>
                    </div>
                  ))}
                  <p className="px-4 py-4 text-xs text-[#526da5]" role="status">
                    {snapshot
                      ? `${snapshot.finished_sections} of ${snapshot.total_sections} analysis sections finished`
                      : 'Reading your document. Your report will open when analysis is finished.'}
                  </p>
                </div>

                <div className="relative mt-5 h-[3px] overflow-hidden bg-[#d9e2f5]">
                  <motion.div
                    animate={{
                      x: [
                        '-100%',
                        '420%',
                      ],
                    }}
                    transition={{
                      duration: 1.5,
                      repeat:
                        Infinity,
                      ease: 'linear',
                    }}
                    className="absolute h-full w-[24%] bg-[#1d4ed8]"
                  />
                </div>
              </div>
            )}
            </>
          </div>
        </Reveal>
      </Container>
    </section>
  )
}

function EngineSection() {
  const items = [
    [
      '01',
      'Parse',
      'Extract readable resume text from PDF, DOCX or TXT.',
    ],
    [
      '02',
      'Retrieve',
      'Use embeddings and BM25 to find relevant resume evidence.',
    ],
    [
      '03',
      'Evaluate',
      'Classify requirements against the retrieved context.',
    ],
    [
      '04',
      'Explain',
      'Turn the structured evaluation into useful feedback.',
    ],
  ]

  return (
    <section id="engine" className="min-h-screen bg-[#1d4ed8] text-white">
      <Container className="grid min-h-screen items-center gap-16 py-20 lg:grid-cols-[0.8fr_1.2fr]">
        <Reveal>
          <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#bfd0ff]">
            05 / Engine
          </div>

          <h2 className="mt-5 text-[43px] font-semibold leading-[1] tracking-[-0.035em] sm:text-[59px]">
            The analysis is a pipeline,
            not one prompt.
          </h2>
        </Reveal>

        <div>
          {items.map(
            (
              [
                number,
                title,
                body,
              ],
              index,
            ) => (
              <motion.div
                key={title}
                initial={{
                  opacity: 0,
                  x: 30,
                }}
                whileInView={{
                  opacity: 1,
                  x: 0,
                }}
                viewport={{
                  once: true,
                }}
                transition={{
                  delay:
                    index *
                    0.08,
                }}
                className="grid gap-3 border-t border-[#6f91e9] py-6 sm:grid-cols-[55px_120px_1fr]"
              >
                <span className="text-[10px] text-[#b0c5ff]">
                  {number}
                </span>

                <span className="text-[15px] font-semibold">
                  {title}
                </span>

                <p className="max-w-[500px] text-[12px] leading-6 text-[#d0dcff]">
                  {body}
                </p>
              </motion.div>
            ),
          )}
        </div>
      </Container>
    </section>
  )
}

function ReportPreview() {
  return (
    <section id="report-preview" className="min-h-screen bg-[#d6e2ff]">
      <Container className="grid min-h-screen items-center gap-14 py-20 lg:grid-cols-2">
        <Reveal>
          <Artwork label="Future generated visual of the AMOLED SkillSync report dashboard showing score, evidence states and requirement rows." />
        </Reveal>

        <Reveal delay={0.08}>
          <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#315ab7]">
            06 / Report
          </div>

          <h2 className="mt-5 text-[43px] font-semibold leading-[1] tracking-[-0.035em] text-[#07142f] sm:text-[59px]">
            Every useful detail gets its own place.
          </h2>

          <p className="mt-7 max-w-[520px] text-[14px] leading-7 text-[#52688f]">
            Strengths, gaps, requirement evidence, recommendations and match metrics move into a dedicated dashboard after analysis.
          </p>

          <p className="mt-5 max-w-[520px] text-[14px] leading-7 text-[#52688f]">
            The homepage stays a product experience. The report becomes an application workspace.
          </p>
        </Reveal>
      </Container>
    </section>
  )
}

function RewriteSection() {
  return (
    <section className="min-h-screen bg-[#06132f] text-white">
      <Container className="grid min-h-screen items-center gap-16 py-20 lg:grid-cols-[0.85fr_1.15fr]">
        <Reveal>
          <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#7197ee]">
            07 / Coming next
          </div>

          <h2 className="mt-5 text-[43px] font-semibold leading-[1] tracking-[-0.035em] sm:text-[59px]">
            Rewrite the section.
            <br />
            Never invent the experience.
          </h2>

          <p className="mt-7 max-w-[510px] text-[14px] leading-7 text-[#91a2c4]">
            SkillSync's next workflow will use the same evidence model to improve summaries, experience bullets, skill ordering and project descriptions.
          </p>
        </Reveal>

        <Reveal delay={0.08}>
          <Artwork
            dark
            label="Future rewrite visual: original resume bullet, detected evidence, rewritten role-specific version."
          />
        </Reveal>
      </Container>
    </section>
  )
}

function PrinciplesSection() {
  const principles = [
    'No invented experience',
    'No keyword stuffing',
    'Evidence before scoring',
    'Requirement-level analysis',
  ]

  return (
    <section className="min-h-screen bg-white">
      <Container className="grid min-h-screen items-center gap-14 py-20 lg:grid-cols-[1fr_1fr]">
        <Reveal>
          <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#315ab7]">
            08 / Product principles
          </div>

          <h2 className="mt-5 max-w-[670px] text-[43px] font-semibold leading-[1] tracking-[-0.035em] text-[#07142f] sm:text-[59px]">
            The resume should still sound like you.
          </h2>
        </Reveal>

        <Reveal delay={0.08}>
          <div>
            {principles.map(
              (
                item,
                index,
              ) => (
                <motion.div
                  key={item}
                  initial={{
                    opacity: 0,
                    x: 25,
                  }}
                  whileInView={{
                    opacity: 1,
                    x: 0,
                  }}
                  viewport={{
                    once: true,
                  }}
                  transition={{
                    delay:
                      index *
                      0.08,
                  }}
                  className="grid grid-cols-[48px_1fr] border-t border-[#ced9f0] py-6"
                >
                  <span className="text-[10px] font-semibold text-[#7890bf]">
                    0{index + 1}
                  </span>

                  <span className="text-[20px] font-semibold tracking-[-0.03em] text-[#18366f]">
                    {item}
                  </span>
                </motion.div>
              ),
            )}
          </div>
        </Reveal>
      </Container>
    </section>
  )
}

function FinalCta() {
  return (
    <section className="min-h-[70vh] bg-[#154fd4] text-white">
      <Container className="flex min-h-[70vh] items-center py-20">
        <Reveal>
          <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#bdd1ff]">
            09 / Your next application
          </div>

          <h2 className="mt-5 max-w-[980px] text-[48px] font-semibold leading-[0.96] tracking-[-0.045em] sm:text-[69px] lg:text-[80px]">
            Know exactly what the resume proves.
          </h2>

          <a
            href="#analyzer"
            className="mt-10 inline-flex items-center gap-3 bg-white px-6 py-4 text-[13px] font-semibold text-[#1544b4]"
          >
            Analyze resume
            <ArrowRight size={16} />
          </a>
        </Reveal>
      </Container>
    </section>
  )
}

function Footer() {
  return (
    <footer className="bg-[#020817] py-16 text-white">
      <Container>
        <div className="grid gap-12 border-b border-[#1c2947] pb-14 sm:grid-cols-2 lg:grid-cols-[1.5fr_1fr_1fr_1fr]">
          <div>
            <div className="text-[21px] font-semibold tracking-[-0.04em]">
              SkillSync
            </div>

            <p className="mt-4 max-w-[300px] text-[11px] leading-5 text-[#7486ad]">
              Evidence-first resume intelligence.
            </p>
          </div>

          {[
            [
              'PRODUCT',
              [
                'Analyzer',
                'Report',
                'Rewrite studio',
              ],
            ],
            [
              'TECHNOLOGY',
              [
                'Hybrid retrieval',
                'Embeddings',
                'Structured output',
              ],
            ],
            [
              'COMPANY',
              [
                'About',
                'Privacy',
                'Contact',
              ],
            ],
          ].map(
            ([title, links]) => (
              <div key={title}>
                <div className="mb-5 text-[9px] font-semibold tracking-[0.15em] text-[#566993]">
                  {title}
                </div>

                <div className="space-y-3">
                  {links.map(
                    (item) => (
                      <div
                        key={item}
                        className="text-[11px] text-[#9caccc]"
                      >
                        {item}
                      </div>
                    ),
                  )}
                </div>
              </div>
            ),
          )}
        </div>

        <div className="flex flex-col gap-3 pt-7 text-[10px] text-[#596c96] sm:flex-row sm:justify-between">
          <span>
            © 2026 SkillSync
          </span>

          <span>
            Built around evidence.
          </span>
        </div>
      </Container>
    </footer>
  )
}

const offerLetterImage =
  new URL(
    '../../resources/images/offer_letter.png',
    import.meta.url,
  ).href


export default function HomePage() {
  const navigate = useNavigate()
  const handleComplete =
    (analysisId) => {
      navigate(`/report?analysis=${encodeURIComponent(analysisId)}`, { state: { analysisId } })
    }

  return (
    <div>
      <Header />

      <main>
        <Hero />
      <OfferSection />
        <MovingRail />
        <WhySection />
        <EvidenceSection />

        <Analyzer
          onComplete={
            handleComplete
          }
        />

        <EngineSection />
        <ReportPreview />
        <RewriteSection />
        <PrinciplesSection />
        <FinalCta />
      </main>

      <Footer />
    </div>
  )
}
