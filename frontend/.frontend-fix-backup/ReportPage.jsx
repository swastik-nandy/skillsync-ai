import {
  ArrowLeft,
  CheckCircle2,
  CircleAlert,
  Lightbulb,
} from 'lucide-react'
import {
  motion,
} from 'framer-motion'
import {
  useEffect,
  useState,
} from 'react'
import {
  Link,
  Navigate,
  useLocation,
} from 'react-router-dom'

import Header from '../components/Header'

const API_URL =
  import.meta.env.VITE_API_URL ||
  'http://localhost:8000'

const terminalStatuses = new Set([
  'completed',
  'completed_with_errors',
  'failed',
])


function Metric({
  label,
  value,
  color,
}) {
  return (
    <div className="border-r border-t border-[#182238] bg-[#05070b] p-6">
      <div className="text-[9px] font-semibold uppercase tracking-[0.15em] text-[#5b6577]">
        {label}
      </div>

      <div
        className={`mt-8 text-[48px] font-semibold leading-none tracking-[-0.04em] ${color}`}
      >
        {value}
      </div>
    </div>
  )
}


export default function ReportPage() {
  const location =
    useLocation()

  const analysisId =
    new URLSearchParams(location.search).get('analysis') ||
    location.state?.analysisId ||
    sessionStorage.getItem(
      'skillsync_analysis_id',
    )

  const [snapshot, setSnapshot] =
    useState(() => {
      const raw =
        sessionStorage.getItem(
          'skillsync_analysis_snapshot',
        )

      if (!raw) {
        return null
      }

      try {
        const cached =
          JSON.parse(raw)

        return cached.analysis_id === analysisId
          ? cached
          : null
      } catch {
        return null
      }
    })

  const [requestError, setRequestError] =
    useState('')

  useEffect(() => {
    if (!analysisId) {
      return undefined
    }

    sessionStorage.setItem(
      'skillsync_analysis_id',
      analysisId,
    )

    let cancelled = false
    let timer = null

    const poll = async () => {
      try {
        const response =
          await fetch(
            `${API_URL}/analysis/${analysisId}`,
          )

        const data =
          await response.json()

        if (!response.ok) {
          throw new Error(
            data?.detail ||
            'Unable to load analysis',
          )
        }

        if (cancelled) {
          return
        }

        setSnapshot(data)
        setRequestError('')

        sessionStorage.setItem(
          'skillsync_analysis_snapshot',
          JSON.stringify(data),
        )

        if (
          !terminalStatuses.has(
            data.status,
          )
        ) {
          timer = setTimeout(
            poll,
            900,
          )
        }
      } catch (error) {
        if (cancelled) {
          return
        }

        setRequestError(
          error.message ||
          'Unable to load analysis',
        )

        timer = setTimeout(
          poll,
          1800,
        )
      }
    }

    poll()

    return () => {
      cancelled = true

      if (timer) {
        clearTimeout(timer)
      }
    }
  }, [analysisId])

  if (!analysisId) {
    return (
      <Navigate
        to="/#analyzer"
        replace
      />
    )
  }

  const sections =
    snapshot?.sections || {}

  const result =
    sections.feedback?.result ||
    {}

  const feedbackReady =
    Boolean(
      sections.feedback?.result
    )

  const overall =
    sections.overall_role_alignment
      ?.result ||
    null

  const skills =
    sections.skills_alignment
      ?.result
      ?.assessment ||
    null

  const experience =
    sections.experience_fit
      ?.result
      ?.assessment ||
    null

  const evidence =
    sections.evidence_quality
      ?.result
      ?.assessment ||
    null

  const documentHealth =
    sections.document_health
      ?.result
      ?.assessment ||
    null

  const projects =
    sections.project_relevance
      ?.result
      ?.assessment ||
    null

  const qualification =
    sections.qualification_alignment
      ?.result
      ?.assessment ||
    null

  const analysisComplete =
    snapshot &&
    terminalStatuses.has(
      snapshot.status,
    )

  const requirements =
    Array.isArray(
      result.requirements,
    )
      ? result.requirements
      : []

  const suggestions =
    Array.isArray(
      result.suggestions,
    )
      ? result.suggestions
      : []

  const supported =
    requirements.filter(
      (item) =>
        item.status ===
        'SUPPORTED',
    )

  const partial =
    requirements.filter(
      (item) =>
        item.status ===
        'PARTIAL',
    )

  const missing =
    requirements.filter(
      (item) =>
        item.status ===
        'NOT_EVIDENCED',
    )

  const strengths =
    supported.map(
      (item) =>
        item.requirement,
    )

  const gaps = [
    ...partial,
    ...missing,
  ].map(
    (item) =>
      item.requirement,
  )

  const statusColor = (
    status,
  ) => {
    if (
      status ===
      'SUPPORTED'
    ) {
      return 'text-emerald-400'
    }

    if (
      status ===
      'PARTIAL'
    ) {
      return 'text-amber-400'
    }

    return 'text-rose-400'
  }

  return (
    <div className="min-h-screen bg-[#020408] text-white">
      <Header dark />

      <main className="py-14 sm:py-18">
        <div className="mx-auto w-[calc(100%-32px)] max-w-[1240px] sm:w-[calc(100%-48px)]">
          <Link
            to="/#analyzer"
            className="inline-flex items-center gap-2 text-[10px] font-semibold text-[#7484a6]"
          >
            <ArrowLeft size={13} />
            New analysis
          </Link>

          <div className="mt-10 grid gap-8 border-b border-[#182238] pb-10 lg:grid-cols-[1fr_auto] lg:items-end">
            <div>
              <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-blue-400">
                Intelligence report
              </div>

              <h1 className="mt-3 text-[44px] font-semibold leading-[0.98] tracking-[-0.04em] sm:text-[60px]">
                Application dashboard.
              </h1>
            </div>

            <div className="text-[10px] font-semibold uppercase tracking-[0.15em] text-emerald-400">
              {analysisComplete
                ? snapshot.status.replaceAll(
                    '_',
                    ' ',
                  )
                : snapshot
                  ? `${snapshot.finished_sections}/${snapshot.total_sections} sections resolved`
                  : 'Starting analysis'}
            </div>
          </div>

          <div className="grid border-l border-[#182238] md:grid-cols-2 xl:grid-cols-4">
            <Metric
              label="Match score"
              value={
                overall?.overall_role_alignment_score != null
                  ? `${overall.overall_role_alignment_score}%`
                  : result.match_percentage != null
                    ? `${result.match_percentage}%`
                    : '—'
              }
              color="text-blue-400"
            />

            <Metric
              label="Supported"
              value={
                feedbackReady
                  ? supported.length
                  : '—'
              }
              color="text-emerald-400"
            />

            <Metric
              label="Partial"
              value={
                feedbackReady
                  ? partial.length
                  : '—'
              }
              color="text-amber-400"
            />

            <Metric
              label="Not evidenced"
              value={
                feedbackReady
                  ? missing.length
                  : '—'
              }
              color="text-rose-400"
            />
          </div>

          {requestError && (
            <div className="border-x border-b border-[#47202a] bg-[#12070a] px-6 py-4 text-[10px] text-rose-300">
              Connection issue: {requestError}. Retrying automatically.
            </div>
          )}

          <div className="grid border-l border-t border-[#182238] sm:grid-cols-2 xl:grid-cols-6">
            {[
              [
                'Skills',
                skills?.skills_alignment_score,
              ],
              [
                'Experience',
                experience?.experience_fit_score,
              ],
              [
                'Evidence',
                evidence?.evidence_quality_score,
              ],
              [
                'Projects',
                projects?.projects_relevance_score,
              ],
              [
                'Qualifications',
                qualification?.qualification_score,
              ],
              [
                'Document health',
                documentHealth?.document_health_score,
              ],
            ].map(
              ([label, score]) => (
                <div
                  key={label}
                  className="border-b border-r border-[#182238] bg-[#05070b] p-4"
                >
                  <div className="text-[8px] font-semibold uppercase tracking-[0.13em] text-[#5b6577]">
                    {label}
                  </div>

                  <div className="mt-3 text-[22px] font-semibold tracking-[-0.04em] text-[#dce4f2]">
                    {score == null
                      ? '—'
                      : `${score}%`}
                  </div>
                </div>
              ),
            )}
          </div>

          <div className="grid border-l border-t border-[#182238] lg:grid-cols-2">
            {[
              [
                'Strengths',
                strengths,
                CheckCircle2,
                'text-emerald-400',
              ],
              [
                'Evidence gaps',
                gaps,
                CircleAlert,
                'text-rose-400',
              ],
            ].map(
              ([
                title,
                items,
                Icon,
                color,
              ]) => (
                <section
                  key={title}
                  className="border-b border-r border-[#182238] bg-[#05070b] p-6"
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      size={17}
                      className={color}
                    />

                    <h2 className="text-[14px] font-semibold">
                      {title}
                    </h2>
                  </div>

                  <div className="mt-5">
                    {items.map(
                      (
                        item,
                        index,
                      ) => (
                        <div
                          key={`${item}-${index}`}
                          className="grid grid-cols-[36px_1fr] border-t border-[#172033] py-4"
                        >
                          <span className="text-[9px] font-semibold text-[#58657a]">
                            {String(
                              index +
                                1,
                            ).padStart(
                              2,
                              '0',
                            )}
                          </span>

                          <span className="text-[11px] leading-5 text-[#b6c0d1]">
                            {item}
                          </span>
                        </div>
                      ),
                    )}
                  </div>
                </section>
              ),
            )}
          </div>

          <section className="border border-[#182238] bg-[#05070b]">
            <div className="grid grid-cols-[50px_1fr_125px] border-b border-[#182238] px-4 py-3 text-[9px] font-semibold uppercase tracking-[0.13em] text-[#596478] sm:grid-cols-[70px_1fr_170px]">
              <span>#</span>
              <span>
                Requirement / evidence
              </span>
              <span>
                Status
              </span>
            </div>

            {requirements.map(
              (
                item,
                index,
              ) => (
                <motion.div
                  key={`${item.requirement}-${index}`}
                  initial={{
                    opacity: 0,
                    y: 14,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                  transition={{
                    delay:
                      index *
                      0.035,
                  }}
                  className="grid grid-cols-[50px_1fr_125px] border-b border-[#151e30] px-4 py-5 last:border-0 sm:grid-cols-[70px_1fr_170px]"
                >
                  <span className="text-[9px] text-[#526078]">
                    {String(
                      index + 1,
                    ).padStart(
                      2,
                      '0',
                    )}
                  </span>

                  <div className="pr-5">
                    <div className="text-[12px] font-medium leading-5 text-[#d9e0ec]">
                      {
                        item.requirement
                      }
                    </div>

                    <p className="mt-2 max-w-[760px] text-[10px] leading-5 text-[#697487]">
                      {item.evidence ||
                        'No explicit evidence found.'}
                    </p>
                  </div>

                  <span
                    className={`text-[9px] font-semibold ${statusColor(item.status)}`}
                  >
                    {item.status
                      ?.replaceAll(
                        '_',
                        ' ')}
                  </span>
                </motion.div>
              ),
            )}
          </section>

          <section className="grid border-x border-b border-[#182238] lg:grid-cols-[260px_1fr]">
            <div className="border-b border-[#182238] bg-[#070a10] p-6 lg:border-b-0 lg:border-r">
              <Lightbulb
                size={18}
                className="text-blue-400"
              />

              <h2 className="mt-5 text-[17px] font-semibold">
                Recommended actions
              </h2>
            </div>

            <div className="bg-[#05070b] px-6">
              {suggestions.map(
                (
                  suggestion,
                  index,
                ) => (
                  <div
                    key={`${suggestion}-${index}`}
                    className="grid grid-cols-[40px_1fr] border-b border-[#172033] py-5 last:border-0"
                  >
                    <span className="text-[9px] font-semibold text-blue-400">
                      {String(
                        index + 1,
                      ).padStart(
                        2,
                        '0',
                      )}
                    </span>

                    <p className="text-[11px] leading-5 text-[#aeb8ca]">
                      {suggestion}
                    </p>
                  </div>
                ),
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}
