import { useQuery } from '@tanstack/react-query';
import { fetchJson } from './client.ts';
import { CompanyFundamentalsResponse, CompetitorBenchmarkResponse } from '../types/micro.ts';

export function useCompanyFundamentals(ticker: string | null) {
  return useQuery<CompanyFundamentalsResponse>({
    queryKey: ['fundamentals', ticker],
    queryFn: () => fetchJson<CompanyFundamentalsResponse>(`/companies/${encodeURIComponent(ticker!)}/fundamentals`),
    enabled: Boolean(ticker),
    staleTime: 1000 * 60 * 15, // 15 mins
  });
}

export function useCompetitorBenchmark(ticker: string | null, metric: string = 'operating_margin') {
  return useQuery<CompetitorBenchmarkResponse>({
    queryKey: ['benchmark', ticker, metric],
    queryFn: () =>
      fetchJson<CompetitorBenchmarkResponse>(
        `/companies/${encodeURIComponent(ticker!)}/benchmark?metric=${encodeURIComponent(metric)}`
      ),
    enabled: Boolean(ticker) && Boolean(metric),
    staleTime: 1000 * 60 * 15,
  });
}
