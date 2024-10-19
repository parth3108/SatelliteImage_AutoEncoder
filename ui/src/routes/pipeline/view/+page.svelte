<script>
	import * as Table from '$lib/components/ui/table/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { onMount } from 'svelte';
	import { Play } from 'lucide-svelte';
	import * as helper from '$lib/internal/helper';
	import API from '$lib/internal/api';

	let pipelines = {};

	let run = [];

	let lastDiv;

	onMount(async () => {
		pipelines = JSON.parse(localStorage.getItem('pipelines')) ?? {};
	});

	let logs = [];

	const runPipeline = async (pipeline, runId) => {
		let parsePipeline = helper.createPipeline(pipeline);

		let reader = await API.runPipeline(parsePipeline, runId);

		while (true) {
			// @ts-ignore
			const { done, value } = await reader?.read();

			if (done) {
				break;
			}

			// Assuming the streamed data is text, convert the chunk to text
			const chunk = new TextDecoder().decode(value);

			// Append the chunk to your output element
			try {
				let parsedChunk = JSON.parse(chunk);
				if (logs.length > 0 && logs[logs.length - 1]['progress']) {
					logs[logs.length - 1]['message'] = parsedChunk;
				} else {
					try {
						if (parsedChunk['success']) {
							logs.push({
								progress: true,
								error: false,
								message: parsedChunk.toString()
							});
						} else {
							if (chunk.toLowerCase().includes('error')) {
								logs.push({
									progress: false,
									error: true,
									message: parsedChunk.toString()
								});
							} else {
								logs.push({
									progress: false,
									error: false,
									message: parsedChunk.toString()
								});
							}
						}
					} catch {
						console.log(parsedChunk);
					}
				}
			} catch {
				if (chunk.toLowerCase().includes('error')) {
					logs.push({
						progress: false,
						error: true,
						message: chunk
					});
				} else {
					logs.push({
						progress: false,
						error: false,
						message: chunk
					});
				}
			}

			lastDiv.scrollIntoView();

			logs = [...logs];
		}
	};
</script>

<div class="flex h-full flex-col">
	<span class="flex min-h-14 flex-row items-center justify-between gap-4 border-b pl-4 pr-8">
		<div class="flex flex-row items-center gap-4">View Pipeline</div>
	</span>
	<div class="m-4 rounded-lg border">
		<Table.Root>
			<Table.Header>
				<Table.Row>
					<Table.Head>Pipeline Name</Table.Head>
					<Table.Head>Pipes</Table.Head>
					<Table.Head></Table.Head>
				</Table.Row>
			</Table.Header>
			<Table.Body>
				{#each Object.keys(pipelines) as pipeline, i (i)}
					<Table.Row>
						<Table.Cell class="font-medium">{pipeline}</Table.Cell>
						<Table.Cell class="">{pipelines[pipeline]['rawPipeline'].length ?? 0}</Table.Cell>
						<Table.Cell class="float-end flex gap-4">
							<Input type="text" class="max-w-64" placeholder="Enter Run ID..." bind:value={run[i]}
							></Input>
							<Button
								class="flex gap-2"
								on:click={() => {
									runPipeline(pipelines[pipeline]['rawPipeline'], run[i]);
								}}
							>
								<Play size={16} />
								Run</Button
							>
						</Table.Cell>
					</Table.Row>
				{/each}
			</Table.Body>
		</Table.Root>
	</div>
	<div class="m-4 flex max-h-full flex-grow flex-col overflow-auto rounded-md border">
		<div bind:this={lastDiv}></div>
		{#each logs.slice().reverse() as log, i (i)}
			{#if log['progress'] === false}
				<div class="border-b p-2">
					{#if log['error']}
						<span class="text-justify text-red-500">{log['message']}</span>
					{:else}
						<span class="text-justify text-green-800">{log['message']}</span>
					{/if}
				</div>
			{:else if log['progress'] === true}
				<div class="flex flex-col border-b p-2">
					<span class="text-green-800">
						Success : {log['message']['success']}/{log['message']['total']}
					</span>
					<span class={log['message']['failed'] > 0 ? 'text-red-500' : ''}>
						Failed : {log['message']['failed']}/{log['message']['total']}
					</span>
				</div>
			{/if}
		{/each}
	</div>
</div>
