# -*- coding: utf-8 -*-

import threading

from tests.base import *

from radish.hookregistry import HookRegistry, before, after
from radish.feature import Feature
from radish.stepmodel import Step
from radish.scenario import Scenario


class HookRegistryTestCase(RadishTestCase):
    """
        Tests for the HookRegistry class
    """
    def test_initializing_hook_registry(self):
        """
            Test the initialization of the hook registry
        """
        empty_hook = {"before": [], "after": []}

        hookregistry = HookRegistry()
        hookregistry.hooks.should.have.length_of(4)
        hookregistry.hooks["all"].should.be.equal(empty_hook)
        hookregistry.hooks["each_feature"].should.be.equal(empty_hook)
        hookregistry.hooks["each_scenario"].should.be.equal(empty_hook)
        hookregistry.hooks["each_step"].should.be.equal(empty_hook)

        HookRegistry.Hook.should.have.property("all")
        HookRegistry.Hook.should.have.property("each_feature")
        HookRegistry.Hook.should.have.property("each_scenario")
        HookRegistry.Hook.should.have.property("each_step")

    def test_register_as_hook(self):
        """
            Test registering function as hook
        """
        empty_hook = {"before": [], "after": []}

        hookregistry = HookRegistry()
        hookregistry.hooks.should.have.length_of(4)
        hookregistry.hooks["all"].should.be.equal(empty_hook)
        hookregistry.hooks["each_feature"].should.be.equal(empty_hook)
        hookregistry.hooks["each_scenario"].should.be.equal(empty_hook)
        hookregistry.hooks["each_step"].should.be.equal(empty_hook)

        hookregistry.hooks["all"]["before"].should.have.length_of(0)
        hookregistry.register("before", "all", "some_func")
        hookregistry.hooks["all"]["before"].should.have.length_of(1)
        hookregistry.hooks["all"]["after"].should.have.length_of(0)

        hookregistry.hooks["each_feature"]["before"].should.have.length_of(0)
        hookregistry.register("before", "each_feature", "some_func")
        hookregistry.hooks["each_feature"]["before"].should.have.length_of(1)
        hookregistry.hooks["each_feature"]["after"].should.have.length_of(0)

        hookregistry.hooks["each_scenario"]["before"].should.have.length_of(0)
        hookregistry.register("before", "each_scenario", "some_func")
        hookregistry.hooks["each_scenario"]["before"].should.have.length_of(1)
        hookregistry.hooks["each_scenario"]["after"].should.have.length_of(0)

        hookregistry.hooks["each_step"]["before"].should.have.length_of(0)
        hookregistry.register("before", "each_step", "some_func")
        hookregistry.hooks["each_step"]["before"].should.have.length_of(1)
        hookregistry.hooks["each_step"]["after"].should.have.length_of(0)

    def test_decorating_with_hook(self):
        """
            Test decorating function as hook
        """
        hookregistry = HookRegistry()

        def some_func():
            pass

        hookregistry.hooks["each_feature"]["before"].should.have.length_of(0)
        before.each_feature(some_func)
        hookregistry.hooks["each_feature"]["before"].should.have.length_of(1)
        hookregistry.hooks["each_feature"]["before"][0][1].should.be.equal(some_func)

        hookregistry.hooks["each_step"]["after"].should.have.length_of(0)
        after.each_step(some_func)
        hookregistry.hooks["each_step"]["after"].should.have.length_of(1)
        hookregistry.hooks["each_step"]["after"][0][1].should.be.equal(some_func)

    def test_calling_registered_hooks(self):
        """
            Test calling registered hooks
        """
        hookregistry = HookRegistry()

        data = threading.local()
        data.called_hooked_a = False
        data.called_hooked_b = False
        data.called_hooked_c = False

        def hooked_a(feature):
            data.called_hooked_a = True

        def hooked_b(step):
            data.called_hooked_b = True

        def hooked_c(feature):
            data.called_hooked_c = True

        before.each_feature(hooked_a)
        after.each_step(hooked_b)
        before.each_feature(hooked_c)

        feature_mock = Mock(spec=Feature)
        feature_mock.all_tags = []
        hookregistry.call("before", "each_feature", feature_mock)
        data.called_hooked_a.should.be.true
        data.called_hooked_b.should.be.false
        data.called_hooked_c.should.be.true

        step_mock = Mock(spec=Step)
        step_mock.all_tags = []
        hookregistry.call("after", "each_step", step_mock)
        data.called_hooked_a.should.be.true
        data.called_hooked_b.should.be.true
        data.called_hooked_c.should.be.true

    def test_calling_registered_hooks_with_arguments(self):
        """
            Test calling registered hooks with arguments
        """
        hookregistry = HookRegistry()

        data = threading.local()
        data.hooked_a_feature = None
        data.hooked_b_step = None
        data.hooked_c_feature = None

        def hooked_a(feature):
            data.hooked_a_feature = feature

        def hooked_b(step):
            data.hooked_b_step = step

        def hooked_c(feature):
            data.hooked_c_feature = feature

        before.each_feature(hooked_a)
        after.each_step(hooked_b)
        before.each_feature(hooked_c)

        feature_mock = Mock(spec=Feature)
        feature_mock.all_tags = []
        step_mock = Mock(spec=Step)
        step_mock.all_tags = []

        hookregistry.call("before", "each_feature", feature_mock)
        data.hooked_a_feature.should.be.equal(feature_mock)
        data.hooked_b_step.should.be.none
        data.hooked_c_feature.should.be.equal(feature_mock)

        hookregistry.call("after", "each_step", step_mock)
        data.hooked_b_step.should.be.equal(step_mock)

    def test_tag_specific_hooks(self):
        """
        Test calling tag specific hooks
        """
        hookregistry = HookRegistry()

        data = threading.local()
        data.before_good_feature = None
        data.before_bad_feature = None
        data.after_step = None
        data.cleanup_feature = None


        def before_good(feature):
            data.before_good_feature = feature

        def before_bad(feature):
            data.before_bad_feature = feature

        def after_step(step):
            data.after_step = step

        def cleanup_feature(feature):
            data.cleanup_feature = feature


        mock_good_case_tag = Mock()
        mock_good_case_tag.name = 'good_case'
        mock_bad_case_tag = Mock()
        mock_bad_case_tag.name = 'bad_case'
        mock_needs_cleanup_tag = Mock()
        mock_needs_cleanup_tag.name = 'needs_cleanup'


        good_feature = Feature(1, "Feature", "Some feature", None, None, tags=[mock_good_case_tag])
        bad_feature = Feature(2, "Feature", "Some feature", None, None, tags=[mock_bad_case_tag, mock_needs_cleanup_tag])
        scenario = Scenario(1, "Scenario", "Some Scenario", None, None, good_feature, tags=[])
        step = Step(1, "Some Step", None, None, scenario, None)

        scenario.steps.append(step)

        before.each_feature(on_tags='good_case')(before_good)
        before.each_feature(on_tags='bad_case')(before_bad)
        after.each_step(on_tags='good_case')(after_step)
        after.each_feature(on_tags='needs_cleanup')(cleanup_feature)

        hookregistry.call("before", "each_feature", good_feature)
        data.before_good_feature.should.be.equal(good_feature)
        data.before_bad_feature.should.be.none
        data.after_step.should.be.none
        data.cleanup_feature.should.be.none
        data.before_good_feature = None

        hookregistry.call("before", "each_feature", bad_feature)
        data.before_good_feature.should.be.none
        data.before_bad_feature.should.be.equal(bad_feature)
        data.after_step.should.be.none
        data.cleanup_feature.should.be.none
        data.before_bad_feature = None

        hookregistry.call("after", "each_step", step)
        data.before_good_feature.should.be.none
        data.before_bad_feature.should.be.none
        data.after_step.should.be.equal(step)
        data.cleanup_feature.should.be.none
        data.after_step = None

        hookregistry.call("after", "each_feature", bad_feature)
        data.before_good_feature.should.be.none
        data.before_bad_feature.should.be.none
        data.after_step.should.be.none
        data.cleanup_feature.should.be.equal(bad_feature)
        data.cleanup_feature = None
