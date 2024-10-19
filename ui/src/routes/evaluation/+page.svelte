<script lang="js">
	import { ChartScatter } from 'lucide-svelte';
	import * as Command from '$lib/components/ui/command/index.js';
	import * as Popover from '$lib/components/ui/popover/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { cn } from '$lib/utils.js';
	import { Check } from 'svelte-radix';
	import { CaretSort } from 'svelte-radix';
	import { onMount, tick } from 'svelte';
	import API from '$lib/internal/api';
	import { Label } from '$lib/components/ui/label/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import ViewImage from '$lib/internal/components/view-image.svelte';
	import MetricsInterpret from '$lib/internal/components/metrics-interpret.svelte';

	let runIdOpen = false;
	let runIdValue = '';
	let runIds = [];

	$: runIdSelectedValue = runIds.find((f) => f === runIdValue) ?? 'Select Run ID...';

	let evaluationIdOpen = false;
	let evaluationIdValue = '';
	let evaluationIds = [];

	$: evaluationIdSelectedValue =
		evaluationIds.find((f) => f === evaluationIdValue) ?? 'Select Evaluation ID...';

	let results = [];

	const closeAndFocusTriggerForRunId = (triggerId) => {
		runIdOpen = false;
		tick().then(() => {
			let ele = document.getElementById(triggerId);
			ele.click();

			try {
				getEvaluationIds();
			} catch (error) {
				console.error(error);
			}

			try {
				getResultsByRunID();
			} catch (error) {
				console.error(error);
			}
		});
	};

	const closeAndFocusTriggerForEvaluationId = (triggerId) => {
		evaluationIdOpen = false;
		tick().then(() => {
			let ele = document.getElementById(triggerId);
			ele.click();
		});
	};

	onMount(async () => {
		const response = await API.getRunIds();
		if (response?.isSuccess) {
			runIds.push(...response.data);
			runIds = [...runIds];
		}
	});

	let columns = [];
	let selectedColumns = [];

	const getResultsByRunID = async () => {
		evaluationIds = [];
		const response = await API.getEvaluationResults(runIdValue);
		results = [];
		if (response?.isSuccess) {
			await response.data.forEach((result) => {
				if (result['results'] !== null) {
					let tempEvaluationResult = JSON.parse(result['results']);
					Object.keys(tempEvaluationResult).forEach((key) => {
						result[`evaluation_${key}`] = tempEvaluationResult[key];
					});
				}
				delete result['results'];
				results.push(result);
			});
			results = [...results];

			columns = Object.keys(results[0]);

			selectedColumns = Object.keys(results[0]).filter((key) => {
				if (key === 'run_id' || key === 'evaluation_id') {
					return false;
				}

				if (key.includes('evaluation_')) {
					return false;
				}

				return true;
			});
		}
	};

	const getEvaluationIds = async () => {
		evaluationIds = [];
		const response = await API.getEvaluationIds(runIdValue);

		if (response?.isSuccess) {
			console.log(response.data);
			evaluationIds.push(...response.data);
			evaluationIds = [...evaluationIds];
		} else {
			alert('No Evaluation found. Please Run Evaluation first.');
			evaluationIds = [];
			evaluationIdValue = '';
			evaluationIdOpen = false;
		}
	};

	const bytesToSize = (bytes) => {
		const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
		if (bytes === null || bytes === undefined) return '0 Byte';
		if (bytes === 0) return '0 Byte';
		const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
		return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
	};

	const microSecondsToMiliseconds = (nanoSeconds) => {
		return (nanoSeconds / 1000).toFixed(2) + ' ms';
	};
</script>

<div class="flex h-full flex-col">
	<span class="flex min-h-14 items-center gap-4 border-b pl-4 pr-8">
		<ChartScatter size="24" />
		Evaluation
	</span>
	<div class="flex w-full flex-row justify-between">
		<div class="flex flex-col items-start gap-2 p-4">
			<Label>Run ID:</Label>
			<Popover.Root bind:runIdOpen let:ids>
				<Popover.Trigger asChild let:builder>
					<Button
						builders={[builder]}
						variant="outline"
						role="combobox"
						aria-expanded={runIdOpen}
						class="w-[200px] justify-between"
					>
						{runIdSelectedValue}
						<CaretSort class="ml-2 h-4 w-4 shrink-0 opacity-50" />
					</Button>
				</Popover.Trigger>
				<Popover.Content class="w-[200px] p-0">
					<Command.Root>
						<Command.Input placeholder="Search Run ID..." class="h-9" />
						<Command.Empty>No Run ID found.</Command.Empty>
						<Command.Group>
							{#each runIds as runId}
								<Command.Item
									value={runId}
									onSelect={(currentValue) => {
										runIdValue = currentValue;
										closeAndFocusTriggerForRunId(ids.trigger);
									}}
								>
									<Check class={cn('mr-2 h-4 w-4', runIdValue !== runId && 'text-transparent')} />
									{runId}
								</Command.Item>
							{/each}
						</Command.Group>
					</Command.Root>
				</Popover.Content>
			</Popover.Root>
		</div>

		{#if evaluationIds.length > 0}
			<div class="flex flex-col items-start justify-between gap-2 p-4">
				<Label>Evaluation ID:</Label>
				<Popover.Root bind:evaluationIdOpen let:ids>
					<Popover.Trigger asChild let:builder>
						<Button
							builders={[builder]}
							variant="outline"
							role="combobox"
							aria-expanded={evaluationIdOpen}
							class="w-[300px] justify-between"
						>
							{evaluationIdSelectedValue}
							<CaretSort class="ml-2 h-4 w-4 shrink-0 opacity-50" />
						</Button>
					</Popover.Trigger>
					<Popover.Content class="w-[300px] p-0">
						<Command.Root>
							<Command.Input placeholder="Search Evaluation ID..." class="h-9" />
							<Command.Empty>No Evaluation ID found.</Command.Empty>
							<Command.Group>
								{#each evaluationIds as evaluationId}
									<Command.Item
										value={evaluationId}
										onSelect={(currentValue) => {
											evaluationIdValue = currentValue;
											closeAndFocusTriggerForEvaluationId(ids.trigger);
										}}
									>
										<Check
											class={cn(
												'mr-2 h-4 w-4',
												evaluationIdValue !== evaluationId && 'text-transparent'
											)}
										/>
										{evaluationId}
									</Command.Item>
								{/each}
							</Command.Group>
						</Command.Root>
					</Popover.Content>
				</Popover.Root>
			</div>
		{/if}
	</div>
	{#if results.length > 0}
		<span class="flex min-h-14 items-center justify-between border-b border-t pl-4 pr-8">
			Results
			<div class="flex items-center gap-8">
				<MetricsInterpret />
				<span class="text-sm text-gray-500">Total: {results.length}</span>
			</div>
		</span>
		<div class="m-4 max-h-full flex-grow overflow-auto rounded-lg border">
			<Table.Root>
				<Table.Header>
					<Table.Row>
						{#each selectedColumns as column}
							<Table.Head class="text-nowrap text-left"
								>{column
									.split('_')
									.map((c) => {
										if (c !== 'path') {
											return c.charAt(0).toUpperCase() + c.slice(1);
										}
									})
									.join(' ')}</Table.Head
							>
						{/each}
						{#if !evaluationIdSelectedValue.includes('Select Evaluation ID...')}
							{#each Object.keys(results[0][`evaluation_${evaluationIdSelectedValue}`]) as column}
								<Table.Head class="text-nowrap text-left"
									>{column
										.split('_')
										.map((c) => {
											if (c !== 'path') {
												return c.charAt(0).toUpperCase() + c.slice(1);
											}
										})
										.join(' ')}</Table.Head
								>
							{/each}
						{/if}
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each results as result}
						<Table.Row>
							{#each selectedColumns as column}
								{#if column.includes('_size')}
									<Table.Cell>{bytesToSize(result[column])}</Table.Cell>
								{:else if column.includes('_path') && result[column]}
									<Table.Cell>
										<ViewImage
											name="Image {result[column].split('/')[result[column].split('/').length - 1]}"
											path={result[column]}
										></ViewImage>
									</Table.Cell>
								{:else if column.includes('_path') && !result[column]}
									<Table.Cell>No Image Found</Table.Cell>
								{:else if column.includes('_time')}
									<Table.Cell>{microSecondsToMiliseconds(result[column])}</Table.Cell>
								{:else}
									<Table.Cell>{result[column]}</Table.Cell>
								{/if}
							{/each}
							{#if !evaluationIdSelectedValue.includes('Select Evaluation ID...')}
								{#each Object.keys(results[0][`evaluation_${evaluationIdSelectedValue}`]) as column}
									<Table.Cell
										>{result[`evaluation_${evaluationIdSelectedValue}`][column]?.toFixed(3) ??
											null}</Table.Cell
									>
								{/each}
							{/if}
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
		</div>
	{/if}
</div>
