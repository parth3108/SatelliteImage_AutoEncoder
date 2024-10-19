<script>
	import { Input } from '$lib/components/ui/input/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Save, Delete, Check, Search, Plus } from 'lucide-svelte';
	import API from '$lib/internal/api';
	import * as Command from '$lib/components/ui/command/index.js';
	import * as Popover from '$lib/components/ui/popover/index.js';
	import { CaretSort } from 'svelte-radix';
	import { cn } from '$lib/utils.js';
	import * as helper from '$lib/internal/helper';

	import { onMount, tick } from 'svelte';

	let modules = {};

	let rawPipeline = [];
	let pipeline = {};

	let moduleOpen = false;
	let methodOpen = false;

	const getModules = async () => {
		const response = await API.getModules();
		let baseModules = {};
		if (response?.isSuccess) {
			baseModules = response.data;
		}

		await Object.keys(baseModules).forEach((key) => {
			getMethods(key, baseModules[key]);
		});

		modules = modules;
	};

	const getMethods = async (module, value) => {
		const response = await API.getMethods(module);

		if (response?.isSuccess) {
			modules[module] = {};
			modules[module]['module'] = value;
			modules[module]['methods'] = response.data;
		}
	};

	onMount(() => {
		getModules();
	});

	const addPipe = () => {
		rawPipeline.push({
			module: '',
			method: '',
			parameters: []
		});

		rawPipeline = [...rawPipeline];
	};

	const addParamToPipe = (index, params) => {
		rawPipeline[index]['parameters'] = [];
		Object.keys(params['parameters']).forEach((el) => {
			rawPipeline[index]['parameters'].push({
				field: el,
				type: params['parameters'][el],
				value: ''
			});
		});

		rawPipeline = [...rawPipeline];
	};

	const closeAndFocusTriggerForModule = (triggerId) => {
		moduleOpen = false;
		tick().then(() => {
			let ele = document.getElementById(triggerId);
			ele.click();
		});
	};

	const closeAndFocusTriggerForMethod = (triggerId) => {
		moduleOpen = false;
		tick().then(() => {
			let ele = document.getElementById(triggerId);
			ele.click();
		});
	};

	const validatePipe = async (index) => {
		let parsedPipe = helper.createPipe(rawPipeline[index]);
		const response = await API.validatePipe(parsedPipe);

		if (response?.isSuccess) {
			alert('Valid !!!');
		}
	};

	const validatePipeline = async () => {
		let parsedPipeline = helper.createPipeline(rawPipeline);

		const response = await API.validatePipe(parsedPipeline);

		if (response?.isSuccess) {
			alert('Valid !!!');
		}
	};

	const removePipe = async (index) => {
		rawPipeline.splice(index, 1);
		rawPipeline = [...rawPipeline];
	};

	const search = async () => {
		if (
			pipeline['pipelineName'] === null ||
			pipeline['pipelineName'] === undefined ||
			pipeline['pipelineName'] === ''
		) {
			alert('Please Enter Pipeline Name');
			return;
		} else {
			let ls = JSON.parse(localStorage.getItem('pipelines')) ?? {};

			if (ls[pipeline['pipelineName']]) {
				rawPipeline = ls[pipeline['pipelineName']]['rawPipeline'] ?? [];
			} else {
				alert('Pipeline not found');
			}
		}
	};

	const savePipeline = () => {
		if (
			pipeline['pipelineName'] === null ||
			pipeline['pipelineName'] === undefined ||
			pipeline['pipelineName'] === ''
		) {
			alert('Please Enter Pipeline Name');
			return;
		} else {
			pipeline['rawPipeline'] = rawPipeline;

			let ls = JSON.parse(localStorage.getItem('pipelines')) ?? {};

			ls[pipeline['pipelineName']] = pipeline;

			localStorage.setItem('pipelines', JSON.stringify(ls));

			alert('Saved');
		}
	};
</script>

<div class="flex h-full flex-col">
	<span class="flex min-h-14 flex-row items-center justify-between gap-4 border-b pl-4 pr-8">
		<div class="flex flex-row items-center gap-4">
			Edit Pipeline:
			<Input
				type="text"
				bind:value={pipeline['pipelineName']}
				placeholder="Pipeline Name"
				class="w-64"
			/>
			<Button variant="outline" class="flex gap-2" on:click={() => search()}>
				<Search size={18} />
				Search</Button
			>
			<Button
				variant="outline"
				class="flex gap-2"
				on:click={() => {
					savePipeline();
				}}
			>
				<Save size={18} />
				Save</Button
			>
		</div>
		<div class="flex flex-row items-center gap-4">
			<Button variant="destructive" class="flex gap-2" on:click={() => (rawPipeline = [])}>
				<Delete size={18} />Clear</Button
			>
			<Button variant="default" class="flex gap-2" on:click={() => validatePipeline()}>
				<Check size={18} />Validate</Button
			>
		</div>
	</span>
	<div class="flex h-full w-full flex-grow flex-col overflow-auto px-4 pb-4">
		{#each rawPipeline as pipe, i (i)}
			<div class="flex flex-col gap-4 border-b py-4 pl-4 pr-8">
				<div class="flex flex-row items-center gap-4">
					<Popover.Root bind:moduleOpen let:ids>
						<Popover.Trigger asChild let:builder>
							<Button
								builders={[builder]}
								variant="outline"
								role="combobox"
								aria-expanded={moduleOpen}
								class="w-[200px] justify-between"
							>
								{pipe['module'] === '' ? 'Select Module' : modules[pipe['module']]['module']}
								<CaretSort class="ml-2 h-4 w-4 shrink-0 opacity-50" />
							</Button>
						</Popover.Trigger>
						<Popover.Content class="w-[200px] p-0">
							<Command.Root>
								<Command.Input placeholder="Search Module.." class="h-9" />
								<Command.Empty>No Module found.</Command.Empty>
								<Command.Group>
									{#each Object.keys(modules) as module}
										<Command.Item
											value={module}
											onSelect={(currentValue) => {
												pipe['module'] = currentValue;
												pipe['method'] = '';
												pipe['parameters'] = [];
												closeAndFocusTriggerForModule(ids.trigger);
											}}
										>
											<Check
												class={cn('mr-2 h-4 w-4', pipe['module'] !== module && 'text-transparent')}
											/>
											{modules[module]['module']}
										</Command.Item>
									{/each}
								</Command.Group>
							</Command.Root>
						</Popover.Content>
					</Popover.Root>
					{#if pipe['module'] != ''}
						<Popover.Root bind:methodOpen let:ids>
							<Popover.Trigger asChild let:builder>
								<Button
									builders={[builder]}
									variant="outline"
									role="combobox"
									aria-expanded={methodOpen}
									class="w-[200px] justify-between"
								>
									{pipe['method'] === ''
										? 'Select Method'
										: pipe['method']
												.split('_')
												.map((c) => {
													return c.charAt(0).toUpperCase() + c.slice(1);
												})
												.join(' ')}
									<CaretSort class="ml-2 h-4 w-4 shrink-0 opacity-50" />
								</Button>
							</Popover.Trigger>
							<Popover.Content class="w-[200px] p-0">
								<Command.Root>
									<Command.Input placeholder="Search Method.." class="h-9" />
									<Command.Empty>No Method found.</Command.Empty>
									<Command.Group>
										{#each Object.keys(modules[pipe['module']]['methods']) as method}
											<Command.Item
												value={method}
												onSelect={(currentValue) => {
													pipe['method'] = currentValue;
													addParamToPipe(i, modules[pipe['module']]['methods'][currentValue]);
													closeAndFocusTriggerForModule(ids.trigger);
												}}
											>
												<Check
													class={cn(
														'mr-2 h-4 w-4',
														pipe['method'] !== method && 'text-transparent'
													)}
												/>
												{method
													.split('_')
													.map((c) => {
														return c.charAt(0).toUpperCase() + c.slice(1);
													})
													.join(' ')}
											</Command.Item>
										{/each}
									</Command.Group>
								</Command.Root>
							</Popover.Content>
						</Popover.Root>
					{/if}
					<Button variant="destructive" on:click={() => removePipe(i)}>Remove</Button>
					{#if pipe['parameters'].length > 0}
						<Button variant="secondary" on:click={() => validatePipe(i)}>Validate</Button>
					{/if}
				</div>
				{#if pipe['parameters'].length > 0}
					<div class="flex flex-col gap-4">
						{#each pipe['parameters'] as param, j (j)}
							<div>
								<Label
									>{param['field']
										.split('_')
										.map((c) => {
											return c.charAt(0).toUpperCase() + c.slice(1);
										})
										.join(' ')} ( {param['type']} )
								</Label>
								<Input
									type="text"
									placeholder={param['field']
										.split('_')
										.map((c) => {
											return c.charAt(0).toUpperCase() + c.slice(1);
										})
										.join(' ')}
									bind:value={pipe['parameters'][j]['value']}
								/>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/each}

		<Button variant="outline" class="mt-4 flex gap-2" on:click={() => addPipe()}>
			<Plus size={18} />
			Add</Button
		>
	</div>
</div>
