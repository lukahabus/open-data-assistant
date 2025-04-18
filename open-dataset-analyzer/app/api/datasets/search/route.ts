import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query } = body;

    if (!query) {
      return NextResponse.json({ error: "Query is required" }, { status: 400 });
    }

    // Query the DCAT backend
    const response = await fetch(`${process.env.DCAT_API_URL}/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error("Failed to query datasets");
    }

    const datasets = await response.json();

    // Transform datasets to match frontend schema
    const transformedDatasets = datasets.map((dataset: any) => ({
      id: dataset["@id"],
      title: dataset["dct:title"],
      description: dataset["dct:description"],
      modified: dataset["dct:modified"],
      publisher: {
        name: dataset["dct:publisher"]?.["foaf:name"],
      },
    }));

    return NextResponse.json(transformedDatasets);
  } catch (error) {
    console.error("Error searching datasets:", error);
    return NextResponse.json(
      { error: "Failed to search datasets" },
      { status: 500 }
    );
  }
}
