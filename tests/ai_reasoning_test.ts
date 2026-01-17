
/**
 * AI Reasoning Test Suite
 * Verifies the "Smart Routing" capabilities of the UnifiedIntelligenceService.
 * 
 * Usage: 
 * 1. Ensure backend is running (localhost:8000)
 * 2. Run: npx ts-node tests/ai_reasoning_test.ts
 */

import crypto from 'crypto';

const API_URL = "http://localhost:8000/api/ai-chat/chat";

// Mock implementation of fetch for environment without it (if older node)
// checking availability first
if (typeof fetch === "undefined") {
    console.error("This test requires Node.js v18+ with native fetch");
    process.exit(1);
}

interface TestResult {
    name: string;
    passed: boolean;
    details: string;
    duration: number;
}

async function runTest(name: string, query: string, expectedType: "internal" | "external" | "hybrid" | "chat"): Promise<TestResult> {
    console.log(`\n🧪 Requesting: "${query}"...`);
    const start = Date.now();

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: query,
                session_id: `test-${crypto.randomUUID()}`
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
        }

        const data: any = await response.json();
        const duration = Date.now() - start;

        console.log(`   ✅ Response in ${duration}ms`);
        console.log(`   📝 Answer: ${data.response?.substring(0, 100)}...`);
        console.log(`   🔍 Classification: ${data.classification?.type}`);

        // Analyze sources
        const sources = data.sources || [];
        const hasInternal = sources.some((s: any) => s.type === 'internal');
        const hasExternal = sources.some((s: any) => s.type === 'external');

        let valid = false;
        let reason = "";

        if (expectedType === "internal") {
            valid = hasInternal;
            reason = hasInternal ? "Correctly used SQL" : "Failed to use SQL";
        } else if (expectedType === "external") {
            valid = hasExternal;
            reason = hasExternal ? "Correctly used Web Search" : "Failed to use Web Search";
        } else if (expectedType === "hybrid") {
            valid = hasInternal && hasExternal;
            reason = valid ? "Correctly used BOTH SQL and Web Search" : `Missing sources. Internal: ${hasInternal}, External: ${hasExternal}`;
        } else {
            valid = true; // Chat doesn't strictly require sources
            reason = "Chat completed";
        }

        return {
            name,
            passed: valid,
            details: reason,
            duration
        };

    } catch (error: any) {
        return {
            name,
            passed: false,
            details: `Exception: ${error.message}`,
            duration: Date.now() - start
        };
    }
}

async function main() {
    console.log("🚀 Starting AI Reasoning Tests");
    console.log("Target: " + API_URL);

    const results: TestResult[] = [];

    // 1. Internal Logic Test
    results.push(await runTest(
        "Internal Data Query",
        "Сколько мы продали в мае 2025?",
        "internal"
    ));

    // 2. External Logic Test
    results.push(await runTest(
        "External Market Query",
        "Почему упал спрос на молочку в Минске? Найди новости.",
        "external"
    ));

    // 3. Hybrid Logic Test (Critical)
    results.push(await runTest(
        "Hybrid Reasoning Query",
        "Сравни наши продажи (в базе) с инфляцией в Беларуси (в интернете) за этот год.",
        "hybrid"
    ));

    console.log("\n\n📊 TEST SUMMARY");
    console.log("=================");

    let passed = 0;
    for (const res of results) {
        const icon = res.passed ? "✅" : "❌";
        console.log(`${icon} ${res.name}: ${res.details} (${res.duration}ms)`);
        if (res.passed) passed++;
    }

    console.log("=================");
    console.log(`Total: ${results.length}, Passed: ${passed}, Failed: ${results.length - passed}`);

    if (passed !== results.length) {
        console.log("\n⚠️ Note: Tests may fail if API keys are not configured in .env");
        process.exit(1);
    }
}

main();
